# coding:utf-8

import pymongo
import uuid
from AsppServer.mock_data import mock_task_documents_doc_user_results


class DatabaseConfig:
    def __init__(self):
        self.connection = pymongo.MongoClient('10.214.224.142', 20000)
        self.database = self.connection['aspp_server']
        self.user_collection = self.database['users']
        self.algorithm_collection = self.database['algorithms']
        self.tag_collection = self.database['tags']
        self.task_collection = self.database['tasks']
        self.source_document_collection = self.database['source_documents']
        self.doc_annotation_step = self.database['doc_annotation_step']

        self.document_collection = self.database['documents']
        self.doc_algo_results = self.database['doc_algo_results']
        self.doc_user_results = self.database['doc_user_results']
        self.doc_experts_results = self.database['doc_experts_results']

    @staticmethod
    def get_global_str_id() -> str:
        return str(uuid.uuid4())


class UserService:
    def __init__(self):
        self.dbConfig = DatabaseConfig()
        self._user_collection = self.dbConfig.user_collection
        self._get_global_str_id = self.dbConfig.get_global_str_id

    def create_user(self, username, pwd, role='normal'):
        if self._user_collection.count({'username': username}) > 0:
            return 'user existed'

        u = {
            '_id': self._get_global_str_id(),
            'username': username,
            'password': pwd,
            'role': role,
        }
        self._user_collection.insert_one(u)
        del u['password']
        return u

    def check_user_password(self, username, pwd) -> dict:
        return self._user_collection.find_one({'username': username, 'password': pwd}, {'password': 0})

    def get_users(self, uid):
        if uid is not None:
            return self._user_collection.find_one({'_id': uid}, {'password': 0})

        res = []
        for u in self._user_collection.find({}, {'password': 0}):
            res.append(u)
        return res


class AdminService:
    def __init__(self):
        self.dbConfig = DatabaseConfig()
        self._tag_collection = self.dbConfig.tag_collection
        self._source_document_collection = self.dbConfig.source_document_collection
        self._doc_annotation_step = self.dbConfig.doc_annotation_step
        self._task_collection = self.dbConfig.task_collection
        self._algorithm_collection = self.dbConfig.algorithm_collection
        self._get_global_str_id = self.dbConfig.get_global_str_id

    def add_algorithm(self, algo):
        algo['_id'] = self._get_global_str_id()
        self._algorithm_collection.insert_one(algo)
        return algo

    def update_algorithm(self, algo_id, algo):
        self._algorithm_collection.update_one({'_id': algo_id}, {'$set': algo})
        return algo

    def del_algorithm(self, algo_id):
        # TODO 正在使用的不能删除
        self._algorithm_collection.delete_one({'_id': algo_id})

    def get_algorithms(self, algo_id):
        if algo_id is not None:
            return self._algorithm_collection.find_one({'_id': algo_id})

        res = []
        for i in self._algorithm_collection.find():
            res.append(i)
        return res

    def add_tag(self, tag: dict):
        tag['_id'] = self._get_global_str_id()
        self._tag_collection.insert_one(tag)
        return tag

    def update_tag(self, tag_id, tag: dict):
        self._tag_collection.update_one({'_id': tag_id}, {'$set': tag})
        return tag

    def del_tag(self, tag_id: str):
        self._tag_collection.delete_one({'_id': tag_id})

    def get_tags(self, tag_id):
        if tag_id is not None:
            return self._tag_collection.find_one({'_id': tag_id})

        tags = []
        for t in self._tag_collection.find():
            tags.append(t)
        return tags

    # def copy_source_corpus_for_task(self, source_doc_list, task_id):
    #     documents = []
    #     for doc in self.dbConfig.source_document_collection.find({'_id': {'$in': source_doc_list}},
    #                                                              {'title': 1, 'content': 1}):
    #         doc['sourceId'] = doc['_id']
    #         doc['_id'] = self._get_global_str_id()
    #
    #         doc['taskId'] = task_id
    #         documents.append(doc)
    #     self._document_collection.insert_many(documents)

    def add_task(self, task: dict):
        task['_id'] = self._get_global_str_id()
        task['status'] = 'annotating'
        self._task_collection.insert_one(task)
        # self.copy_source_corpus_for_task(task['sourceDocuments'], task['_id'])

        # TODO 开启线程将任务中的 documents 在后台自动预标注
        # mock annotated data
        mock_task_documents_doc_user_results(task['_id'])
        return task

    def delete_task(self, task_id):
        # TODO 优雅一点儿。。。
        self._task_collection.delete_one({'_id': task_id})
        self._doc_annotation_step.delete_many({'taskId': task_id})

    def update_task(self, task_id, task: dict):
        self._task_collection.update_one({'_id': task_id}, {'$set': task})
        return task

    def get_tasks(self, task_id):
        if task_id is not None:
            return self._task_collection.find_one({'_id': task_id})

        res = []
        for t in self._task_collection.find():
            res.append(t)
        return res

    def get_source_document_count(self):
        return self._source_document_collection.count()

    def get_source_documents(self, skip=0, limit=10):
        res = []
        for doc in self.dbConfig.source_document_collection.find({}, {'title': 1, 'content': 1}).skip(skip).limit(
                limit):
            res.append(doc)
        return res


class AnnotationService:
    def __init__(self):
        self.dbConfig = DatabaseConfig()
        self._tag_collection = self.dbConfig.tag_collection
        self._source_document_collection = self.dbConfig.source_document_collection
        self._task_collection = self.dbConfig.task_collection
        self._algorithm_collection = self.dbConfig.algorithm_collection
        self._get_global_str_id = self.dbConfig.get_global_str_id
        self._doc_annotation_step = self.dbConfig.doc_annotation_step

        # self._doc_algo_result = self.dbConfig.doc_algo_results
        # self._doc_user_result = self.dbConfig.doc_user_results
        # self._doc_experts_results = self.dbConfig.doc_experts_results

    def get_my_todo_list(self, uid):
        steps = []
        for i in self._doc_annotation_step.find({'annotator.type': 'user', 'annotator._id': uid},
                                                {'taskId': 1, 'docId': 1, 'status': 1, 'stepNo': 1}):
            steps.append(i)

        tasks = self.get_tasks_by_id_list(list(map(lambda x: x['taskId'], steps)))
        docs = self.get_documents_by_id_list(list(map(lambda x: x['docId'], steps)))

        task_dict, doc_dict = {}, {}

        def f1(x):
            task_dict[x['_id']] = x

        def f2(x):
            doc_dict[x['_id']] = x

        map(f1, tasks)
        map(f2, docs)

        res_dict = {}
        for s in steps:
            task_id = s[['taskId']]
            if task_id not in res_dict:
                task_dict['steps'] = []
                res_dict[task_id] = task_dict[task_id]
            res_dict[task_id]['steps'].append({
                '_id': s['_id'],
                'status': s['status'],
                'stepNo': s['stepNo'],
                'docTitle': doc_dict[s['docId']]['title']
            })
        return list(res_dict.values())

    def get_tasks_by_id_list(self, id_list):
        tasks = []
        for t in self._task_collection.find({'_id': {'$in': id_list}}, {'name': 1, 'type': 1, 'status': 1}):
            tasks.append(t)
        return tasks

    def get_documents_by_id_list(self, id_list):
        docs = []
        for d in self._source_document_collection.find({'_id': {'$in': id_list}}, {'title': 1}):
            docs.append(d)
        return docs

    def get_doc_annotation_step(self, step_id):
        step = self._doc_annotation_step.find_one({'_id': step_id})
        

        d = self._doc_user_result.find_one({'docId': doc_id, 'userId': uid})
        detail = self._source_document_collection.find_one({'_id': doc_id})
        res = {
            '_id': doc_id,
            'taskId': d['taskId'],
            'status': d['status'],
            'title': detail['title'],
            'content': detail['content'],
        }
        if 'curStage' not in d or d['curStage'] is None or len(d['curStage']) == 0:
            res['annotations'] = d['preStage']['annotations']
            res['slots'] = d['preStage']['slots']
        else:
            res['annotations'] = d['curStage']['annotations']
            res['slots'] = d['curStage']['slots']
        return res

    def update_annotation(self, doc_id, uid, req):
        status = 'annotating'
        if len(req['slots']) == 0:
            status = "finished"

        self._doc_user_result.update_one(
            {
                'docId': doc_id,
                'userId': uid,
            },
            {
                '$set': {
                    'curStage.annotations': req['annotations'],
                    'curStage.slots': req['slots'],
                    'status': status,
                }
            }
        )

    def get_task(self, task_id):
        return self._task_collection.find_one({'_id': task_id}, {'name': 1, 'type': 1, 'status': 1, 'tags': 1})
