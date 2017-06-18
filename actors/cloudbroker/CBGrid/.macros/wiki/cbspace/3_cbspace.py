from js9 import j
try:
    import ujson as json
except:
    import json


def generateUsersList(objdict, accessUserType, users):
    """
    Generate the list of users that have ACEs on the account

    :param sclient: osis client for system model
    :param objdict: dict with the object data
    :param accessUserType: specifies whether object is account or cloudspace
    :return: list of users have access to cloudspace
    """
    for acl in objdict['acl']:
        if acl['userGroupId'] in [user['name'] for user in users]:
            continue
        if acl['type'] == 'U':
            userq = j.portal.tools.models.system.User.objects(name=acl['userGroupId'])
            if userq.count() > 0:
                userobj = userq.first()
                user = userobj.to_dict()
                user['userstatus'] = acl['status']
                user['id'] = userobj.id
            elif acl['status'] == 'INVITED':
                user = dict()
                user['name'] = acl['userGroupId']
                user['emails'] = [acl['userGroupId']]
                user['userstatus'] = acl['status']
            else:
                user = dict()
                user['name'] = acl['userGroupId']
                user['emails'] = ['N/A']
                user['userstatus'] = 'N/A'
            user['accessUserType'] = accessUserType
            user['acl'] = acl['right']
            users.append(user)
    return users


def main(j, args, params, tags, tasklet):
    models = j.portal.tools.models.cloudbroker
    params.result = (args.doc, args.doc)
    id = args.requestContext.params.get('id')
    if not id:
        args.doc.applyTemplate({})
        return params

    if not models.Cloudspace.exists(id):
        args.doc.applyTemplate({'cloudspace': None}, False)
        return params

    cloudspace = models.Cloudspace.get(id)

    # Resource limits
    j.apps.cloudbroker.account.cb.fillResourceLimits(cloudspace.resourceLimits)

    users = list()
    users = generateUsersList(cloudspace.account, 'acc', users)
    users = generateUsersList(cloudspace, 'cl', users)
    users = generateUsersList(cloudspace, 'cl', users)
    args.doc.applyTemplate({'cloudspace': cloudspace, 'users': users}, False)
    return params
