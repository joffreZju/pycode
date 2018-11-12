# coding:utf-8

from collections import defaultdict
from copy import deepcopy
import json, os, uuid, yaml, pymongo


class DatabaseConfig:
    def __init__(self):
        self.connection = pymongo.MongoClient('10.214.224.142', 20000)
        self.database = self.connection['aspp_server']
        self.user_collection = self.database['users']
        self.algorithm_collection = self.database['algorithms']
        self.tag_collection = self.database['tags']
        self.task_collection = self.database['tasks']
        self.source_document_collection = self.database['annotated_source_data']
        self.document_collection = self.database['documents']
        self.doc_annotation_step = self.database['doc_annotation_step']

        self.doc_algo_results = self.database['doc_algo_results']
        self.doc_user_results = self.database['doc_user_results']
        self.doc_experts_results = self.database['doc_experts_results']

    @staticmethod
    def get_global_str_id() -> str:
        return str(uuid.uuid4())


dbConfig = DatabaseConfig()
source_data_collection = dbConfig.source_document_collection


def etl_source_txt(dir_path='I:/IndoorData/annotation-task/docs/0/'):
    docs = []
    for f_name in os.listdir(dir_path):
        f = open(dir_path + f_name, 'r', encoding='utf-8')
        docs.append({
            '_id': str(uuid.uuid4()),
            'title': f_name,
            'content': [f.read()]
        })
    source_data_collection.insert_many(docs)


def etl_source_annotations(dir_path='I:/IndoorData/annotation-task/annotations/0/'):
    for f_name in os.listdir(dir_path):
        group = f_name.split('.txt.')
        title = group[0] + '.txt'
        f = open(dir_path + f_name, 'r', encoding='utf-8')
        annotations = json.load(f)
        annotations['user'] = group[1]
        annotations['type'] = 'diff' if group[1].find('diff') >= 0 else 'annotation'
        source_data_collection.update_one(
            {'title': title},
            {
                '$push': {
                    'result': annotations
                }
            }
        )
        print(group)


def mock_task_documents_doc_user_results(doc_id_list, task_id=None):
    if task_id is None:
        return

    user_id = '44e45329-677e-46d7-9b29-afa088807925'
    username = 'user-02'

    for docId in doc_id_list:
        for r in dbConfig.source_document_collection.find_one({'_id': docId})['result']:
            if len(r['slots']) > 0:
                dbConfig.doc_annotation_step.insert_one({
                    '_id': str(uuid.uuid4()),
                    'docId': docId,
                    'taskId': task_id,
                    'annotator': {
                        'type': 'algorithm',
                        'name': 'merge 算法',
                        '_id': 'algo-id...'
                    },
                    'annotationResult': {
                        'annotations': r['annotations'],
                        'slots': r['slots']
                    },
                    'stepNo': 2
                })

                dbConfig.doc_annotation_step.insert_one({
                    '_id': str(uuid.uuid4()),
                    'docId': docId,
                    'taskId': task_id,
                    'annotator': {
                        'type': 'user',
                        'name': username,
                        '_id': user_id
                    },
                    'annotationResult': {
                        'annotations': [],
                        'slots': []
                    },
                    'status': 'waiting',
                    'stepNo': 3
                })
                break

    # for doc in dbConfig.source_document_collection.find({}, {'_id': 0}):
    #     doc_id = str(uuid.uuid4())
    #     dbConfig.document_collection.insert_one({
    #         '_id': doc_id,
    #         'title': doc['title'],
    #         'content': doc['content'],
    #         'taskId': task_id,
    #     })
    #
    #     for r in doc['result']:
    #         if len(r['slots']) > 0:
    #             dbConfig.database['doc_user_results'].insert_one({
    #                 'taskId': tid,
    #                 'docId': doc_id,
    #                 'userId': user_id,
    #                 'status': 'waiting',
    #                 'preStage': {
    #                     'annotations': r['annotations'],
    #                     'slots': r['slots']
    #                 },
    #                 'curStage': {}
    #             })
    #             break


def clean_mock_task():
    for task in dbConfig.task_collection.find().skip(0):
        tid = task['_id']
        dbConfig.task_collection.delete_one({'_id': tid})
        dbConfig.document_collection.delete_many({'taskId': tid})
        dbConfig.doc_user_results.delete_many({'taskId': tid})


def load_yaml_tags_to_mongo():
    f = open('./test_files/aspp.yaml', 'r', encoding='utf-8')

    # js = open('./test_files/tag.json', 'w', encoding='utf-8')
    # js.write(json.dumps(yaml.load(f.read()), ensure_ascii=False))

    for t in yaml.load(f.read())['tags']:
        if dbConfig.tag_collection.count({'name': t['name']}) == 0:
            t['type'] = '实体识别'
            t['_id'] = str(uuid.uuid4())
            dbConfig.tag_collection.insert_one(t)


def add_all_tags_for_task():
    tags = []
    for tag in dbConfig.tag_collection.find():
        tags.append(tag)

    dbConfig.task_collection.update_many({}, {'$set': {'tags': tags}})


class Range:
    def __init__(self, b, s, e):
        self.blockIndex = b
        self.startOffset = s
        self.endOffset = e

    @staticmethod
    def dict_to_obj(d):
        r = Range(0, 0, 0)
        r.__dict__.update(d)
        return r


class Diff:
    def __init__(self, t: str, r: Range, distribution: []):
        self.type = t
        self.range = r
        self.distribution = distribution


class Annotation:
    def __init__(self, _id, tp, tag, entity, _range: Range):
        self.id = _id
        self.type = tp
        self.tag = tag
        self.entity = entity
        self.range = _range


class SimpleDiff:
    @staticmethod
    def calculate_diff(annotation_sources):
        """
        :param annotation_sources: {
            'user-1': {
                'annotations': []
            },
            'user-2': {
                'annotations': []
            }
        }
        :return: diff_slots -> []
        """
        source_count = len(annotation_sources)
        items = SimpleDiff.get_annotation_items(annotation_sources)

        null_distribution_dict = {}
        for user in annotation_sources:
            null_distribution_dict[user] = []

        null_range = {
            'blockIndex': -1,
            'startOffset': -1,
            'endOffset': -1,
        }
        diffs, partial_count, distribution_dict = [], {}, deepcopy(null_distribution_dict)
        cur_range, cur_tag, cur_diff_type = deepcopy(null_range), '', ''

        for it in items:
            anno = it['annotation']

            # it 与已有标注的不重叠，更新结果，清空缓存
            if cur_range['blockIndex'] != -1 and (cur_range['blockIndex'] != anno['range']['blockIndex']
                                                  or cur_range['endOffset'] <= anno['range']['startOffset']):
                SimpleDiff.append_one_diff(diffs, cur_range, cur_diff_type, distribution_dict)
                cur_range, cur_tag, cur_diff_type = deepcopy(null_range), '', ''
                distribution_dict = deepcopy(null_distribution_dict)
                partial_count.clear()

            # 新的一轮，重置缓存
            if cur_range['blockIndex'] == -1:
                cur_range.update(anno['range'])
                cur_tag, cur_diff_type = anno['tag'], 'partial'

            distribution_dict[it['username']].append(anno)
            partial_count[it['username']] = True

            # 将 anno append 之后，判断是 consistent/partial/conflict
            if cur_tag == anno['tag'] and SimpleDiff.is_same_range(cur_range, anno['range']):
                if cur_diff_type == 'partial':
                    if len(partial_count) == source_count:
                        cur_diff_type = 'consistent'
                else:
                    SimpleDiff.extend_range(cur_range, anno['range'])
            else:
                cur_diff_type = 'conflict'
                SimpleDiff.extend_range(cur_range, anno['range'])

        SimpleDiff.append_one_diff(diffs, cur_range, cur_diff_type, distribution_dict)
        return diffs

    @staticmethod
    def append_one_diff(diffs, cur_range, cur_diff_type, distribution_dict):
        diffs.append({
            'type': 'slot',
            'id': 'slot-' + str(len(diffs) + 1),
            'slotType': 'diff',
            'range': cur_range,
            'data': {
                'type': cur_diff_type,
                'range': cur_range,
                'distribution': list(distribution_dict.items())
            }
        })

    @staticmethod
    def extend_range(cur_range, another):
        cur_range['startOffset'] = min(cur_range['startOffset'], another['startOffset'])
        cur_range['endOffset'] = max(cur_range['endOffset'], another['endOffset'])

    @staticmethod
    def is_same_range(a, b):
        return a['blockIndex'] == b['blockIndex'] \
               and a['startOffset'] == b['startOffset'] \
               and a['endOffset'] == b['endOffset']

    @staticmethod
    def get_annotation_items(annotation_sources):
        annotation_items = []
        for user in annotation_sources:
            for i in annotation_sources[user]['annotations']:
                annotation_items.append({
                    'username': user,
                    'annotation': i
                })
        annotation_items.sort(key=lambda x: (x['annotation']['range']['blockIndex'],
                                             x['annotation']['range']['startOffset'],
                                             x['annotation']['range']['endOffset']))
        return annotation_items


def majority_voting_merge(slots):
    # 系统已有指标, 这个 acc_map 可以配置为根据用户数目投票，或者根据用户准确率贡献度投票
    user_acc_map = defaultdict(lambda: 1)
    majority_voting_threshold = 0.7

    def is_same_annotation(a1, a2):
        if a1 is None and a2 is None:
            return True
        elif a1 is None or a2 is None:
            return False
        return a1['tag'] == a2['tag'] and a1['range']['blockIndex'] == a2['range']['blockIndex'] and a1['range'][
            'startOffset'] == a2['range']['startOffset'] and a1['range']['endOffset'] == a2['range']['endOffset']

    merged_annotations = []
    conflict_slots = []
    for slo in slots:
        if slo['data']['type'] == 'consistent':
            merged_annotations.append(slo['data']['distribution'][0][1][0])
        elif slo['data']['type'] == 'partial':
            total, partial, annotation = 0, 0, None
            for distr in slo['data']['distribution']:
                total += user_acc_map[distr[0]]
                if len(distr[1]) != 0:
                    partial += user_acc_map[distr[0]]
                    annotation = distr[1][0]
            if partial / total >= majority_voting_threshold:
                merged_annotations.append(annotation)
            else:
                conflict_slots.append(slo)
        else:
            # 基于用户准确率进行多数投票，尽可能解决 conflict
            annotations, score, total = [], [], 0
            for distr in slo['data']['distribution']:
                if len(distr[1]) == 0:
                    distr[1].append(None)
                for distr_anno in distr[1]:
                    total += user_acc_map[distr[0]]
                    for j in range(0, len(annotations)):
                        if is_same_annotation(distr_anno, annotations[j]):
                            score[j] += user_acc_map[distr[0]]
                            break
                    else:
                        annotations.append(distr_anno)
                        score.append(user_acc_map[distr[0]])

            if max(score) / total >= majority_voting_threshold:
                i = score.index(max(score))
                merged_annotations.append(annotations[i])
            else:
                conflict_slots.append(slo)
            # TODO 根据 conflict 和 partial 的处理作为不同的 merge 算法。
            # conflict_slots.append(slo)
    return {
        'annotations': merged_annotations,
        'slots': conflict_slots
    }


if __name__ == '__main__':
    def func0():
        # etl_source_txt()
        # etl_source_annotations()
        clean_mock_task()
        # mock_task_documents_doc_user_results()


    def func1():
        test_1 = json.load(open('./test_files/test-1.json', 'r', encoding='utf-8'))
        test_2 = json.load(open('./test_files/test-2.json', 'r', encoding='utf-8'))

        diff_slots = SimpleDiff.calculate_diff({'test-1': test_1, 'test-2': test_2})

        diff_file = open('./test_files/diff.json', 'w', encoding='utf-8')
        diff_file.write(json.dumps({'annotations': [], 'slots': diff_slots}, ensure_ascii=False))

        merge_res = majority_voting_merge(diff_slots)

        merge_file = open('./test_files/merge.json', 'w', encoding='utf-8')
        merge_file.write(json.dumps(merge_res, ensure_ascii=False))


    def func2():
        wjf_1 = json.load(open('./test_files/test.json.wjf-1.json', 'r', encoding='utf-8'))
        wjf_2 = json.load(open('./test_files/test.json.wjf-2.json', 'r', encoding='utf-8'))
        wjf_3 = json.load(open('./test_files/test.json.wjf-3.json', 'r', encoding='utf-8'))

        diff_slots = SimpleDiff.calculate_diff({'wjf-1': wjf_1, 'wjf-2': wjf_2, 'wjf-3': wjf_3})

        diff_file = open('./test_files/diff.json', 'w', encoding='utf-8')
        diff_file.write(json.dumps({'annotations': [], 'slots': diff_slots}, ensure_ascii=False))

        merge_res = majority_voting_merge(diff_slots)

        merge_file = open('./test_files/merge.json', 'w', encoding='utf-8')
        merge_file.write(json.dumps(merge_res, ensure_ascii=False))
