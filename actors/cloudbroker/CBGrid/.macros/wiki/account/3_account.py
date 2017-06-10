try:
    import ujson as json
except:
    import json


def generateUsersList(sclient, accountdict):
    """
    Generate the list of users that have ACEs on the account

    :param sclient: osis client for system model
    :param accountdict: dict with the account data
    :return: list of users have access to account
    """
    users = list()
    for acl in accountdict['acl']:
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
            user['acl'] = acl['right']
            users.append(user)
    return users


def main(j, args, params, tags, tasklet):
    models = j.portal.tools.models.cloudbroker
    params.result = (args.doc, args.doc)
    id = args.requestContext.params.get('id')

    if not models.Account.exists(id):
        args.doc.applyTemplate({'id': None}, False)
        return params

    accountobj = models.Account.get(id)
    accountdict = accountobj.to_dict()

    accountdict['users'] = generateUsersList(sclient, accountdict)
    j.apps.cloudbroker.account.cb.fillResourceLimits(accountobj.resourceLimits)
    accountdict['reslimits'] = accountobj.resourceLimits

    args.doc.applyTemplate(accountdict, False)
    return params
