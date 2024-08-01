import json
import os 
from fauna import fql
from fauna.client import Client
from fauna.encoding import QuerySuccess
from fauna.errors import FaunaException


FAUNA_KEY = os.environ["FAUNA_KEY"]
FAUNA_COLLECTION = "Tasks"

class DB():
    def __init__(self):
        self.client = Client(secret=FAUNA_KEY)

    def save_task(self, task):
        #del task["script"]
        task["script"] = task["script"].replace("${", "[DOLLAR_CURLY]")
        task_str = json.dumps(task)
        query = fql(FAUNA_COLLECTION+".create("+task_str+")")
        res: QuerySuccess = self.client.query(query)

    def get_task_by_id(self, task_id):
        query = FAUNA_COLLECTION+".byId(\""+task_id+"\")"
        res = self.client.query(fql(query))
        task_doc = res.data
        task = {"fauna_id":task_doc.id}
        for key in task_doc:
            task[key] = task_doc.get(key)
        task["script"]= task["script"].replace("[DOLLAR_CURLY]", "${")
        return task

    def get_all_tasks(self):
        query = FAUNA_COLLECTION+".all()"
        #tasks = self.client.query(fql(query)).data
        pages = self.client.paginate(fql(query))
        tasks = []
        for page in pages:
            for task in page:
                obj = {"fauna_id":task.id}
                for key in task:
                    obj[key] = task.get(key)
                obj["script"]= obj["script"].replace("[DOLLAR_CURLY]", "${")
                tasks.append(obj)
        return tasks

    def get_tasks_by_subject(self, subject):
        tasks = self.get_all_tasks()
        return [t for t in tasks if t["subject"] == subject]

