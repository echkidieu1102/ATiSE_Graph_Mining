# encoding: utf-8
import os
import pandas as pd
import numpy as np
import time
from collections import defaultdict


class KnowledgeGraphYG:
    def __init__(self, data_dir, count=300, rev_set=0):
        self.data_dir = data_dir

        # info about entities and relation
        self.entity_dict = {}
        self.entities = []
        self.relation_dict = {}
        self.n_entity = 0
        self.n_relation = 0

        # info about facts
        self.training_triples = []          # list of triples in the form of (h, t, r)
        self.validation_triples = []
        self.test_triples = []
        self.training_facts = []
        self.validation_facts = []
        self.test_facts = []
        self.n_training_triple = 0
        self.n_validation_triple = 0
        self.n_test_triple = 0

        # 
        self.n_time = 0                     # length of step times
        self.start_year= -500               # init default start year if None (####-##-## ~ YYYY-MM-DD)
        self.end_year = 3000                # init default end year if None (####-##-## ~ YYYY-MM-DD)
        self.year_class=[]                  # list years appear in facts
        self.year2id = dict()               # with keys: time interval, values: index 
        self.rev_set = rev_set              # don't know
        self.fact_count = count             # number of facts to group within a time interval
        self.to_skip_final = {'lhs': {}, 'rhs': {}}         # Example: 'lhs':{(6465, 5, '1952-##-##', '1964-##-##'): {6464}}), 'rhs':, {(6464, 5, '1952-##-##', '1964-##-##'): {6465}})

        '''load dicts and triples'''
        self.time_list()
        self.load_dicts()
        self.load_triples()
        self.load_filters()
        '''construct pools after loading'''
        # self.training_triple_pool = set(self.training_triples)
        # self.golden_triple_pool = set(self.training_triples) | set(self.validation_triples) | set(self.test_triples)

    def load_dicts(self):
        entity_dict_file = 'entity2id.txt'
        relation_dict_file = 'relation2id.txt'
        print('-----Loading entity dict-----')
        entity_df = pd.read_table(os.path.join(self.data_dir, entity_dict_file), header=None)
        self.entity_dict = dict(zip(entity_df[0], entity_df[1]))
        self.n_entity = len(self.entity_dict)
        self.entities = list(self.entity_dict.values())
        print('#entity: {}'.format(self.n_entity))
        print('-----Loading relation dict-----')
        relation_df = pd.read_table(os.path.join(self.data_dir, relation_dict_file), header=None)
        self.relation_dict = dict(zip(relation_df[0], relation_df[1]))
        self.n_relation = len(self.relation_dict)
        if self.rev_set>0: self.n_relation *= 2
        print('#relation: {}'.format(self.n_relation))

    def time_list(self):
        training_file = 'train.txt'
        validation_file = 'valid.txt'
        test_file = 'test.txt'
        triple_file = 'triple2id.txt'
        training_df = pd.read_table(os.path.join(self.data_dir, training_file), header=None)
        training_df = np.array(training_df).tolist()
        validation_df = pd.read_table(os.path.join(self.data_dir, validation_file), header=None)
        validation_df = np.array(validation_df).tolist()
        test_df = pd.read_table(os.path.join(self.data_dir, test_file), header=None)
        test_df = np.array(test_df).tolist()
        # DEBUG
        # training_df = training_df[:50]
        # validation_df = validation_df[:50]
        # test_df = test_df[:25]
        
 #       triple_df = pd.read_table(os.path.join(self.data_dir, triple_file), header=None)
 #       triple_df = np.array(triple_df).tolist()
        triple_df = np.concatenate([training_df,validation_df,test_df],axis=0)
        n=0
        
        year_list=[]
        for triple in triple_df:
            n+=1
            if triple[3][0]=='-':
                start = -int(triple[3].split('-')[1])
                year_list.append(start)
            else:
                start = triple[3].split('-')[0]
                if start =='####':
                    start = self.start_year
                else:
                    start = start.replace('#', '0')
                    start = int(start)
                    year_list.append(start)


            if triple[4][0]=='-':
                end = -int(triple[4].split('-')[1])
                year_list.append(end)
            else:
                end = triple[4].split('-')[0]
                if end =='####':
                    end = self.end_year
                else:
                    end = end.replace('#', '0')
                    end = int(end)
                    year_list.append(end)

#            for i in range(start,end):
#                 year_list.append(i)
            


        year_list.sort()

        freq=defaultdict(int)
        for year in year_list:
            freq[year]=freq[year]+1

        year_class=[]
        count=0
        for key in sorted(freq.keys()):
            count += freq[key]
            if count>=self.fact_count:
                year_class.append(key)
                count=0
        year_class[-1]=year_list[-1]

        year2id = dict()
        prev_year = year_list[0]
        i = 0
        for i, yr in enumerate(year_class): 
            year2id[(prev_year, yr)] = i
 #           if i>2: 
            prev_year = yr + 1

        self.year2id=year2id
        self.year_class = year_class
        self.n_time = len(self.year2id.keys())


    def load_triples(self):
        training_file = 'train.txt'
        validation_file = 'valid.txt'
        test_file = 'test.txt'
        print('-----Loading training triples-----')
        training_df = pd.read_table(os.path.join(self.data_dir, training_file), header=None)
        training_df = np.array(training_df).tolist()
        for triple in training_df:
            if triple[3].split('-')[0] == '####':
                start=self.start_year
                start_idx = 0
            elif triple[3][0] == '-':
                start=-int(triple[3].split('-')[1].replace('#', '0'))
            elif triple[3][0] != '-':
                start = int(triple[3].split('-')[0].replace('#','0'))
            
            if triple[4].split('-')[0] == '####':
                end = self.end_year
                end_idx = self.n_time-1
            elif triple[4][0] == '-':
                end =-int(triple[4].split('-')[1].replace('#', '0'))
            elif triple[4][0] != '-':
                end = int(triple[4].split('-')[0].replace('#','0'))
        
            for key, time_idx in sorted(self.year2id.items(), key=lambda x:x[1]):
                if start>=key[0] and start<=key[1]:
                    start_idx = time_idx
                if end>=key[0] and end<=key[1]:
                    end_idx = time_idx


            self.training_triples.append([triple[0],triple[2],triple[1],start_idx,end_idx])
            self.training_facts.append([triple[0],triple[2],triple[1],triple[3],triple[4]])
            if self.rev_set>0: self.training_triples.append([triple[2],triple[0],triple[1]+self.n_relation//2,start_idx,end_idx])
            # for day_idx in range(start_idx,end_idx+1):
            #     try:
            #         self.training_triples.append([triple[0],triple[2],triple[1],day_idx])
            #     except KeyError:
            #         continue
        self.n_training_triple = len(self.training_triples)
        print('#training triple: {}'.format(self.n_training_triple))
        print('-----Loading validation triples-----')
        validation_df = pd.read_table(os.path.join(self.data_dir, validation_file), header=None)
        validation_df = np.array(validation_df).tolist()
        for triple in validation_df:
            if triple[3].split('-')[0] == '####':
                start=self.start_year
                start_idx = 0
            elif triple[3][0] == '-':
                start=-int(triple[3].split('-')[1].replace('#', '0'))
            elif triple[3][0] != '-':
                start = int(triple[3].split('-')[0].replace('#','0'))
            
            if triple[4].split('-')[0] == '####':
                end = self.end_year
                end_idx = self.n_time-1
            elif triple[4][0] == '-':
                end =-int(triple[4].split('-')[1].replace('#', '0'))
            elif triple[4][0] != '-':
                end = int(triple[4].split('-')[0].replace('#','0'))
        
            for key, time_idx in sorted(self.year2id.items(), key=lambda x:x[1]):
                if start>=key[0] and start<=key[1]:
                    start_idx = time_idx
                if end>=key[0] and end<=key[1]:
                    end_idx = time_idx
            
                    
            self.validation_triples.append([triple[0],triple[2],triple[1],start_idx,end_idx])
            self.validation_facts.append([triple[0],triple[2],triple[1],triple[3],triple[4]])
            # for day_idx in range(start_idx,end_idx+1):
            #     try:
            #         self.validation_triples.append([triple[0],triple[2],triple[1],day_idx])
            #     except KeyError:
            #         continue
        self.n_validation_triple = len(self.validation_triples)
        print('#validation triple: {}'.format(self.n_validation_triple))
        print('-----Loading test triples------')
        test_df = pd.read_table(os.path.join(self.data_dir, test_file), header=None)
        test_df = np.array(test_df).tolist()
        for triple in test_df:
            if triple[3].split('-')[0] == '####':
                start=self.start_year
                start_idx = 0
            elif triple[3][0] == '-':
                start=-int(triple[3].split('-')[1].replace('#', '0'))
            elif triple[3][0] != '-':
                start = int(triple[3].split('-')[0].replace('#','0'))
            
            if triple[4].split('-')[0] == '####':
                end = self.end_year
                end_idx = self.n_time-1
            elif triple[4][0] == '-':
                end =-int(triple[4].split('-')[1].replace('#', '0'))
            elif triple[4][0] != '-':
                end = int(triple[4].split('-')[0].replace('#','0'))
        
            for key, time_idx in sorted(self.year2id.items(), key=lambda x:x[1]):
                if start>=key[0] and start<=key[1]:
                    start_idx = time_idx
                if end>=key[0] and end<=key[1]:
                    end_idx = time_idx
                    

            self.test_triples.append([triple[0],triple[2],triple[1],start_idx,end_idx])
            self.test_facts.append([triple[0],triple[2],triple[1],triple[3],triple[4]])
            # for day_idx in range(start_idx,end_idx+1):
            #     try:
            #         self.test_triples.append([triple[0],triple[2],triple[1],day_idx])
            #     except KeyError:
            #         continue
        self.n_test_triple = len(self.test_triples)
        print('#test triple: {}'.format(self.n_test_triple))

    def load_filters(self):
        print("creating filtering lists")
        to_skip = {'lhs': defaultdict(set), 'rhs': defaultdict(set)}
        facts_pool = [self.training_facts,self.validation_facts,self.test_facts]
        for facts in facts_pool:
            for fact in facts:
                to_skip['lhs'][(fact[1], fact[2],fact[3],fact[4])].add(fact[0])  # left prediction
                to_skip['rhs'][(fact[0], fact[2],fact[3],fact[4])].add(fact[1])  # right prediction
                
        for kk, skip in to_skip.items():
            for k, v in skip.items():
                self.to_skip_final[kk][k] = sorted(list(v))
        print("data preprocess completed")


class KnowledgeGraph:
    def __init__(self, data_dir, gran=1,rev_set=0):
        self.data_dir = data_dir

        # info about entities and relation
        self.entity_dict = {}
        self.gran = gran
        self.entities = []
        self.relation_dict = {}
        self.n_entity = 0
        self.n_relation = 0

        # info about facts
        self.training_triples = []  # list of triples in the form of (h, t, r)
        self.validation_triples = []
        self.test_triples = []
        self.training_facts = []
        self.validation_facts = []
        self.test_facts = []
        self.n_training_triple = 0
        self.n_validation_triple = 0
        self.n_test_triple = 0

        # 
        self.rev_set = rev_set
        self.start_date = '2014-01-01' if self.data_dir == './datasets/icews14' else '2005-01-01'
        self.start_sec = time.mktime(time.strptime(self.start_date,'%Y-%m-%d'))
        self.n_time=365 if self.data_dir == './datasets/icews14' else 4017
        self.to_skip_final = {'lhs': {}, 'rhs': {}}
        '''load dicts and triples'''
        self.load_dicts()
        self.load_triples()
        self.load_filters()
        '''construct pools after loading'''
        # self.training_triple_pool = set(self.training_triples)
        # self.golden_triple_pool = set(self.training_triples) | set(self.validation_triples) | set(self.test_triples)

    def load_dicts(self):
        entity_dict_file = 'entity2id.txt'
        relation_dict_file = 'relation2id.txt'
        print('-----Loading entity dict-----')
        entity_df = pd.read_table(os.path.join(self.data_dir, entity_dict_file), header=None)
        self.entity_dict = dict(zip(entity_df[0], entity_df[1]))
        self.n_entity = len(self.entity_dict)
        self.entities = list(self.entity_dict.values())
        print('#entity: {}'.format(self.n_entity))
        print('-----Loading relation dict-----')
        relation_df = pd.read_table(os.path.join(self.data_dir, relation_dict_file), header=None)
        self.relation_dict = dict(zip(relation_df[0], relation_df[1]))
        self.n_relation = len(self.relation_dict)
        if self.rev_set>0: self.n_relation *= 2
        print('#relation: {}'.format(self.n_relation))

    def load_triples(self):
        training_file = 'train.txt'
        validation_file = 'valid.txt'
        test_file = 'test.txt'
        print('-----Loading training triples-----')
        training_df = pd.read_table(os.path.join(self.data_dir, training_file), header=None)
        training_df = np.array(training_df).tolist()
        for triple in training_df:
            end_sec = time.mktime(time.strptime(triple[3], '%Y-%m-%d'))
            day = int((end_sec - self.start_sec) / (self.gran*24 * 60 * 60))
            self.training_triples.append([self.entity_dict[triple[0]],self.entity_dict[triple[2]],self.relation_dict[triple[1]],day])
            self.training_facts.append([self.entity_dict[triple[0]],self.entity_dict[triple[2]],self.relation_dict[triple[1]],triple[3],0])
            if self.rev_set>0: self.training_triples.append([self.entity_dict[triple[2]],self.entity_dict[triple[0]],self.relation_dict[triple[1]]+self.n_relation//2,day])

        self.n_training_triple = len(self.training_triples)
        print('#training triple: {}'.format(self.n_training_triple))
        print('-----Loading validation triples-----')
        validation_df = pd.read_table(os.path.join(self.data_dir, validation_file), header=None)
        validation_df = np.array(validation_df).tolist()
        for triple in validation_df:
            end_sec = time.mktime(time.strptime(triple[3], '%Y-%m-%d'))
            day = int((end_sec - self.start_sec) / (self.gran*24 * 60 * 60))
            self.validation_triples.append([self.entity_dict[triple[0]],self.entity_dict[triple[2]],self.relation_dict[triple[1]],day])
            self.validation_facts.append([self.entity_dict[triple[0]],self.entity_dict[triple[2]],self.relation_dict[triple[1]],triple[3],0])

        self.n_validation_triple = len(self.validation_triples)
        print('#validation triple: {}'.format(self.n_validation_triple))
        print('-----Loading test triples------')
        test_df = pd.read_table(os.path.join(self.data_dir, test_file), header=None)
        test_df = np.array(test_df).tolist()
        for triple in test_df:
            end_sec = time.mktime(time.strptime(triple[3], '%Y-%m-%d'))
            day = int((end_sec - self.start_sec) / (self.gran*24 * 60 * 60))
            self.test_triples.append(
                    [self.entity_dict[triple[0]], self.entity_dict[triple[2]], self.relation_dict[triple[1]], day])
            self.test_facts.append([self.entity_dict[triple[0]],self.entity_dict[triple[2]],self.relation_dict[triple[1]],triple[3],0])

        self.n_test_triple = len(self.test_triples)
        print('#test triple: {}'.format(self.n_test_triple))


    def load_filters(self):
        print("creating filtering lists")
        to_skip = {'lhs': defaultdict(set), 'rhs': defaultdict(set)}
        facts_pool = [self.training_facts,self.validation_facts,self.test_facts]
        for facts in facts_pool:
            for fact in facts:
                to_skip['lhs'][(fact[1], fact[2],fact[3], fact[4])].add(fact[0])  # left prediction
                to_skip['rhs'][(fact[0], fact[2],fact[3], fact[4])].add(fact[1])  # right prediction
                
        for kk, skip in to_skip.items():
            for k, v in skip.items():
                self.to_skip_final[kk][k] = sorted(list(v))
        print("data preprocess completed")
        
     
if __name__ == "__main__":
    KnowledgeGraphYG(data_dir="./datasets/yago")
    # KnowledgeGraph(data_dir="./datasets/icews14")