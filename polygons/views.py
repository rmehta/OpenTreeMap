import json

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.core.files.base import ContentFile

from django.contrib.auth.decorators import login_required
from django.contrib.gis.geos import Point

from models import TreeRegionPolygon, TreeRegionEntry, DBHClass
from treemap.models import Species

def polygons2dict(polygons):
    polys = {}
    for polygon in polygons:
        entries = TreeRegionEntry.objects.filter(polygon=polygon)

        data = {e.species.pk: {} for e in entries}
        for entry in entries:
            species = data[entry.species.pk]
            species[entry.dbhclass.label] = entry.count

        polys[polygon.pk] = data

    return polys

def polygon_search(request):
    id = request.GET.get('id', None)

    if id:
        polygons = TreeRegionPolygon.objects.filter(pk=id)
    else:
        lat = float(request.GET['lat'])
        lon = float(request.GET['lon'])

        point = Point(lon, lat, srid=4326)

        polygons = TreeRegionPolygon.objects.filter(geometry__contains=point)

    polys = {}

    for polygon in polygons:
        entries = TreeRegionEntry.objects.filter(polygon=polygon,count__gt=0)

        species = list({e.species.pk for e in entries})
        classes = {e.dbhclass.pk: e.dbhclass for e in entries}.values()

        sorted(classes, key=lambda a: a.dbh_min)

        polys[polygon.pk] = {"species": species,
                             "classes": [c.label for c in classes]}

    return HttpResponse(json.dumps(polys),
                        content_type='application/json')

@login_required
def polygon_update(request, polygon_id):
    rep = request.user.reputation

    if rep.reputation < 1000:
        raise PermissionDenied('%s cannot access this view because they do not have the required permission' % request.user.username)

    polygon = TreeRegionPolygon.objects.get(pk=polygon_id)

    all_species = []

    for key in request.POST.keys():
        if key.startswith('pval_'):
            (pgonid, speciesid, dbhid) = key.split('_')[1:]
            if pgonid != polygon_id:
                raise Exception("Invalid polygon id: %s" % pgonid)

            species = Species.objects.get(pk=speciesid)

            t, created = TreeRegionEntry.objects.get_or_create(
                polygon=polygon,
                dbhclass=DBHClass.objects.get(pk=dbhid),
                species=species)

            all_species.append(species)

            t.count = request.POST[key]
            t.save()

    TreeRegionEntry.objects\
                   .filter(polygon=polygon)\
                   .exclude(species__in=all_species)\
                   .delete()

    return HttpResponseRedirect(
        reverse('polygons.views.polygon_view', args=(polygon_id,)))

@login_required
def polygon_edit(request, polygon_id):
    rep = request.user.reputation

    if rep.reputation < 1000:
        raise PermissionDenied('%s cannot access this view because they do not have the required permission' % request.user.username)

    return polygon_view(request, polygon_id, template='polygons/edit.html')

@login_required
def polygon_update_photo(request, polygon_id):
    polygon = TreeRegionPolygon.objects.get(pk=polygon_id)

    rfile = request.FILES['photo']
    file_content = ContentFile(rfile.read())
    fname = rfile.name

    polygon.photo.save(fname, file_content)

    polygon_url = reverse('polygons.views.polygon_view', args=(polygon_id,))
    next_url = request.REQUEST.get('currentpage', polygon_url)

    return HttpResponseRedirect(next_url)


def polygon_view(request, polygon_id,template='polygons/view.html'):

    showedit = request.user and request.user.reputation >= 1000

    polygon = TreeRegionPolygon.objects.get(pk=polygon_id)
    alldbhs = DBHClass.objects.all()

    poly = []
    for (species, dbhs) in polygons2dict([polygon])[polygon.pk].iteritems():
        s = Species.objects.get(pk=species)
        row = [[s.pk,s.scientific_name]]

        for dbh in alldbhs:
            row.append([dbh.pk , dbhs.get(dbh.label,"")])

        poly.append(row)

    return render_to_response(
        template,
        RequestContext(
            request,
            {'showedit': showedit,
             'polygonobj': polygon,
             'polygon': poly,
             'classes': alldbhs}))