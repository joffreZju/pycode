# coding:utf-8

from flask import request, Response, Flask, make_response, jsonify, session, render_template, Blueprint, abort
from AsppServer.service import UserService, AdminService, AnnotationService

admin_app = Blueprint('admin_app', __name__)
annotation_app = Blueprint('annotation_app', __name__)
open_app = Blueprint('open_app', __name__)

userService = UserService()
adminService = AdminService()
annotationService = AnnotationService()


@admin_app.before_request
def admin_decorator():
    if 'uid' not in session:
        return 'login status error', 400

    user = userService.get_users(session.get('uid'))
    if user is None or user['role'] != 'admin':
        return 'user role error', 400


@annotation_app.before_request
def normal_user_decorator():
    if 'uid' not in session:
        return 'login status error', 400


# region admin algorithms 管理

@admin_app.route('/algorithms', methods=['post'])
def add_algorithm():
    req = request.json
    algo = adminService.add_algorithm(req)
    return ''


@admin_app.route('/algorithms/<algorithmId>', methods=['put'])
def update_algorithm(algorithmId):
    req = request.json
    algo = adminService.update_algorithm(algorithmId, req)
    return ''


@admin_app.route('/algorithms/<algorithmId>', methods=['delete'])
def del_algorithm(algorithmId):
    adminService.del_algorithm(algorithmId)
    return ''


@admin_app.route('/algorithms/<algorithmId>', methods=['get'])
def get_algorithm_by_id(algorithmId):
    return adminService.get_algorithms(algorithmId)


@admin_app.route('/algorithms', methods=['get'])
def get_algorithms():
    return adminService.get_algorithms(None)


# endregion


# region admin tags 管理


@admin_app.route('/tags', methods=['post'])
def add_tag():
    tag = adminService.add_tag(request.json)
    return {'success': True, 'data': tag}


@admin_app.route('/tags/<tagId>', methods=['put'])
def update_tag(tagId):
    tag = adminService.update_tag(tagId, request.json)
    return ''


@admin_app.route('/tags/<tagId>', methods=['delete'])
def del_tag(tagId):
    adminService.del_tag(tagId)
    return ''


@admin_app.route('/tags/<tagId>', methods=['get'])
def get_tag_by_id(tagId):
    tag = adminService.get_tags(tagId)
    return tag


@admin_app.route('/tags', methods=['get'])
def get_tags():
    tags = adminService.get_tags(None)
    return tags


# endregion


# region admin task 管理

@admin_app.route('/users')
def get_users():
    return userService.get_users(None)


@admin_app.route('/source-documents', methods=['get'])
def get_source_documents():
    skip = int(request.args.get('skip'))
    limit = int(request.args.get('limit'))
    return adminService.get_source_documents(skip, limit)


@admin_app.route('/source-document-count', methods=['get'])
def get_source_document_count():
    return {'count': adminService.get_source_document_count()}


@admin_app.route('/task-config', methods=['get'])
def get_task_config():
    return {
        'users': userService.get_users(None),
        'algorithms': adminService.get_algorithms(None),
        'tags': adminService.get_tags(None)
    }


@admin_app.route('/tasks', methods=['post'])
def add_task():
    req = request.json
    resp = adminService.add_task(req)
    return ''


@admin_app.route('/tasks/<taskId>', methods=['put'])
def update_task(taskId):
    resp = adminService.update_task(taskId, request.json)
    return ''


@admin_app.route('/tasks/<taskId>', methods=['delete'])
def del_task(taskId):
    adminService.delete_task(taskId)
    return ''


@admin_app.route('/tasks/<taskId>', methods=['get'])
def get_task_by_id(taskId):
    task = adminService.get_task_by_id(taskId)
    if task is None:
        return 'task not exist', 400
    return task


@admin_app.route('/tasks', methods=['get'])
def get_tasks():
    tasks = adminService.get_tasks()
    if tasks is None or len(tasks) == 0:
        return []
    return tasks


@admin_app.route('/tasks/<taskId>/remove-docs', methods=['delete'])
def remove_docs_from_task(taskId):
    docs_ids = request.json
    pass


@admin_app.route('/tasks/<taskId>/append-docs', methods=['post'])
def append_docs_from_task(taskId):
    pass


# endregion


# region 登录注册

@open_app.route('/sign-up', methods=['POST'])
def sign_up():
    req = request.json
    r = userService.create_user(req['username'], req['password'], req['role'])

    if type(r) is dict:
        if 'uid' in session:
            session.pop('uid')
        session.setdefault('uid', r['_id'])
        return r
    return r, 400


@open_app.route('/sign-in', methods=['POST'])
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


@open_app.route('/logout')
def logout():
    session.pop('uid', None)
    return ''


@open_app.route('/myinfo', methods=['get'])
def get_my_info():
    if 'uid' not in session:
        return {
            'role': 'anonymous'
        }
    return userService.get_users(session.get('uid'))


# endregion


# region 用户标注

@annotation_app.route('/todo-tasks', methods=['get'])
def get_todo_tasks():
    return annotationService.get_my_todo_list(session.get('uid'))


@annotation_app.route('/tasks/<taskId>', methods=['get'])
def get_task(taskId):
    return annotationService.get_task(taskId)


@annotation_app.route('/annotation-steps/<stepId>', methods=['get'])
def get_annotation_step(stepId):
    return annotationService.get_doc_annotation_step(stepId)


@annotation_app.route('/annotation-steps/<stepId>', methods=['put'])
def update_annotation_step(stepId):
    annotationService.update_doc_annotation_step(stepId, request.json)
    return ''


@annotation_app.route('/annotation-steps/<stepId>/submit', methods=['post'])
def submit_annotation_step(stepId):
    res = annotationService.submit_doc_annotation_step(stepId)
    if res is None:
        return ''
    else:
        return res, 400


# endregion


class JsonResponse(Response):
    @classmethod
    def force_type(cls, response, environ=None):
        if isinstance(response, (list, dict)):
            response = jsonify(response)
        return super(Response, cls).force_type(response, environ)


main_app = Flask(__name__)
main_app.secret_key = 'session_secret_key'
main_app.response_class = JsonResponse

main_app.register_blueprint(admin_app, url_prefix='/api/admin')
main_app.register_blueprint(annotation_app, url_prefix='/api')
main_app.register_blueprint(open_app, url_prefix='/api')


@main_app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    main_app.run(host="0.0.0.0", port=9000)
