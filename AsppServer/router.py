# coding:utf-8

from flask import request, Response, Flask, make_response, jsonify, session, render_template
from AsppServer.service import UserService, AdminService, AnnotationService


class JsonResponse(Response):
    @classmethod
    def force_type(cls, response, environ=None):
        if isinstance(response, (list, dict)):
            response = jsonify(response)
        return super(Response, cls).force_type(response, environ)


app = Flask(__name__)
app.secret_key = 'session_secret_key'
app.response_class = JsonResponse

userService = UserService()
adminService = AdminService()
annotationService = AnnotationService()


# ********************* algorithms 管理 **********************

@app.route('/api/admin/algorithms', methods=['post'])
def add_algorithm():
    req = request.json
    algo = adminService.add_algorithm(req)
    return ''


@app.route('/api/admin/algorithms/<algorithmId>', methods=['put'])
def update_algorithm(algorithmId):
    req = request.json
    algo = adminService.update_algorithm(algorithmId, req)
    return ''


@app.route('/api/admin/algorithms/<algorithmId>', methods=['delete'])
def del_algorithm(algorithmId):
    adminService.del_algorithm(algorithmId)
    return ''


@app.route('/api/admin/algorithms/<algorithmId>', methods=['get'])
def get_algorithm_by_id(algorithmId):
    return adminService.get_algorithms(algorithmId)


@app.route('/api/admin/algorithms', methods=['get'])
def get_algorithms():
    return adminService.get_algorithms(None)


# ********************* user 管理 **********************

@app.route('/api/admin/users')
def get_users():
    return userService.get_users(None)


# ********************* tags 管理 **********************


@app.route('/api/admin/tags', methods=['post'])
def add_tag():
    tag = adminService.add_tag(request.json)
    return {'success': True, 'data': tag}


@app.route('/api/admin/tags/<tagId>', methods=['put'])
def update_tag(tagId):
    tag = adminService.update_tag(tagId, request.json)
    return ''


@app.route('/api/admin/tags/<tagId>', methods=['delete'])
def del_tag(tagId):
    adminService.del_tag(tagId)
    return ''


@app.route('/api/admin/tags/<tagId>', methods=['get'])
def get_tag_by_id(tagId):
    tag = adminService.get_tags(tagId)
    return tag


@app.route('/api/admin/tags', methods=['get'])
def get_tags():
    tags = adminService.get_tags(None)
    return tags


# ********************* task 管理 **********************

@app.route('/api/admin/tasks', methods=['post'])
def add_task():
    req = request.json
    resp = adminService.add_task(req)
    return ''


@app.route('/api/admin/tasks/<taskId>', methods=['put'])
def update_task(taskId):
    resp = adminService.update_task(taskId, request.json)
    return ''


@app.route('/api/admin/tasks/<taskId>', methods=['delete'])
def del_task(taskId):
    adminService.delete_task(taskId)
    return ''


@app.route('/api/admin/tasks/<taskId>', methods=['get'])
def get_task_by_id(taskId):
    task = adminService.get_tasks(taskId)
    if task is None:
        return 'task not exist', 400
    return task


@app.route('/api/admin/tasks', methods=['get'])
def get_tasks():
    tasks = adminService.get_tasks(None)
    if tasks is None or len(tasks) == 0:
        return 'there is no task', 400
    return tasks


@app.route('/api/admin/source-documents', methods=['get'])
def get_source_documents():
    skip = int(request.args.get('skip'))
    limit = int(request.args.get('limit'))
    return adminService.get_source_documents(skip, limit)


@app.route('/api/admin/source-document-count', methods=['get'])
def get_source_document_count():
    return {'count': adminService.get_source_document_count()}


@app.route('/api/admin/task-config', methods=['get'])
def get_task_config():
    return {
        'users': userService.get_users(None),
        'algorithms': adminService.get_algorithms(None),
        'tags': adminService.get_tags(None)
    }


# ********************* 登录注册 **********************

@app.route('/api/sign-up', methods=['POST'])
def sign_up():
    req = request.json
    r = userService.create_user(req['username'], req['password'], req['role'])

    if type(r) is dict:
        if 'uid' in session:
            session.pop('uid')
        session.setdefault('uid', r['_id'])
        return r
    return r, 400


@app.route('/api/sign-in', methods=['POST'])
def sign_in():
    req = request.json
    user = userService.check_user_password(req['username'], req['password'])

    if user is not None:
        if 'uid' in session:
            session.pop('uid')

        session.setdefault('uid', user['_id'])
        return user
    else:
        return 'wrong username or password!', 400


@app.route('/api/logout')
def logout():
    session.pop('uid', None)
    return ''


@app.route('/api/myinfo', methods=['get'])
def get_my_info():
    if 'uid' not in session:
        return {
            'role': 'anonymous'
        }
    return userService.get_users(session.get('uid'))


# ********************* 标注任务 **********************

@app.route('/api/todo-list', methods=['get'])
def get_my_todo_list():
    if 'uid' not in session:
        return 'login status error', 400
    return annotationService.get_my_todo_list(session.get('uid'))


@app.route('/api/annotation-step/<stepId>', methods=['get'])
def get_document(documentId):
    if 'uid' not in session:
        return 'login status error', 400
    return annotationService.get_document(documentId, session.get('uid'))


@app.route('/api/documents/<documentId>', methods=['put'])
def update_annotation(documentId):
    if 'uid' not in session:
        return 'login status error', 400
    annotationService.update_annotation(documentId, session.get('uid'), request.json)
    return ''


@app.route('/api/submit-document/<documentId>', methods=['post'])
def submit_document():
    annotationService
    pass


@app.route('/api/tasks/<taskId>')
def get_task(taskId):
    return annotationService.get_task(taskId)


# ********************* some test **********************

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/test', methods=['get', 'post', 'put', 'delete'])
def test():
    print(request.args)
    print(session)

    if 'uid' in session:
        return session.get('uid')
    else:
        return 'not login'


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9001)
