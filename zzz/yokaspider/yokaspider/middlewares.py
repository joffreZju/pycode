# -*- coding: utf-8 -*-
import random
from user_agents import agents

class UserAgentMiddleware(object):

    def process_request(self, request, spider):
        agent = random.choice(agents)
        request.headers["User-Agent"] = agent