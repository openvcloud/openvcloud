from js9 import j


def generateUsersList(obj, accessUserType, users):
    """
    Generate the list of users that have ACEs on the account

    :param sclient: osis client for system model
    :param objdict: dict with the object data
    :param accessUserType: specifies whether object is account, vmachine or cloudspace
    :return: list of users have access to vmachine
    """
    models = j.portal.tools.models.system
    for ace in obj.acl:
        if ace.userGroupId in [user['name'] for user in users]:
            continue
        if ace.type == 'U':
            userobj = models.User.objects(name=ace.userGroupId).first()
            if userobj:
                user = userobj.to_dict()
                user['userstatus'] = ace.status
                user['id'] = userobj.id
            elif ace.status == 'INVITED':
                user = dict()
                user['name'] = ace.userGroupId
                user['emails'] = [ace.userGroupId]
                user['userstatus'] = ace.status
            else:
                user = dict()
                user['name'] = ace.userGroupId
                user['emails'] = ['N/A']
                user['userstatus'] = 'N/A'
            user['acl'] = ace.right
            user['accessUserType'] = accessUserType
            users.append(user)
    return users


def main(j, args, params, tags, tasklet):
    models = j.portal.tools.models.cloudbroker
    params.result = (args.doc, args.doc)
    machineId = args.requestContext.params.get('id')
    if not machineId:
        args.doc.applyTemplate({})
        return params

    machine = models.VMachine.get(machineId)
    if not machine:
        args.doc.applyTemplate({})
        return params

    users = list()
    users = generateUsersList(machine.cloudspace.account, 'acc', users)
    users = generateUsersList(machine.cloudspace, 'cl', users)
    users = generateUsersList(machine, 'vm', users)

    args.doc.applyTemplate({'vmachine': machine, 'users': users}, False)
    return params


def match(j, args, params, tags, tasklet):
    return True
