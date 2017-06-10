try:
    import ujson as json
except:
    import json


def generateUsersList(sclient, objdict, accessUserType, users):
    """
    Generate the list of users that have ACEs on the account

    :param sclient: osis client for system model
    :param objdict: dict with the object data
    :param accessUserType: specifies whether object is account or cloudspace
    :return: list of users have access to cloudspace
    """
    for acl in objdict['acl']:
        if acl['userGroupId'] in [user['id'] for user in users]:
            continue
        if acl['type'] == 'U':
            eusers = sclient.user.simpleSearch({'id': acl['userGroupId']})
            if eusers:
                user = eusers[0]
                user['userstatus'] = acl['status']
            elif acl['status'] == 'INVITED':
                user = dict()
                user['id'] = acl['userGroupId']
                user['emails'] = [acl['userGroupId']]
                user['userstatus'] = acl['status']
            else:
                user = dict()
                user['id'] = acl['userGroupId']
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
        args.doc.applyTemplate({'id': None}, False)
        return params

    cloudspaceobj = models.Cloudspace.get(id)

    # Resource limits

    j.apps.cloudbroker.account.cb.fillResourceLimits(cloudspaceobj.resourceLimits)

    users = list()
    users = generateUsersList(sclient, account, 'acc', users)
    cloudspacedict['users'] = generateUsersList(sclient, cloudspacedict, 'cl', users)
    if cloudspacedict['stackId']:
        cloudspacedict['stackName'] = cbclient.stack.get(cloudspacedict['stackId']).name
    args.doc.applyTemplate(cloudspacedict, False)
    return params


def match(j, args, params, tags, tasklet):
    return True
