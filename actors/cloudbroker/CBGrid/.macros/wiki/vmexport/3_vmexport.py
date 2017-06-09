try:
    import ujson as json
except:
    import json
import pprint

def main(j, args, params, tags, tasklet):

    id = args.getTag('id')
    if not id:
        out = 'Missing vmexport id param "id"'
        params.result = (out, args.doc)
        return params
    
    id = int(id)
    cbclient = j.clients.osis.getNamespace('cloudbroker')

    if not cbclient.vmexport.exists(id):
        params.result = ('VMExport with id %s not found' % id, args.doc)
        return params

    vmexportobj = cbclient.vmexport.get(id)
    
    vmexport = vmexportobj.dump()
    vmexport['timestamp'] = j.base.time.epoch2HRDateTime(vmexport['timestamp']) if not vmexport['timestamp']==0 else 'N/A'
    
    vmexport['config'] = pprint.pformat(json.loads(vmexport['config']))
    args.doc.applyTemplate(vmexport, True)

    params.result = (args.doc, args.doc)
    return params

def match(j, args, params, tags, tasklet):
    return True
