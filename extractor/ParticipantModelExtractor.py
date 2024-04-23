from dto.ContractModel import ParticipantsModel
import spacy
from utils.TextUtils import find_distance


class ParticipantModelExtractor:
    def __init__(self, nlp, ner_model):
        self.__nlp = nlp
        self.__ner_model = ner_model

    def __extract_participants(self, doc):
        orgs = {}
        for sent in doc.sents:
            res = self.__ner_model([sent.text])
            sent_orgs = []
            org_index = -1
            for i in range(len(res[0][0])):
                word = res[0][0][i]
                tag = res[1][0][i]
                if tag == 'B-ORG':
                    sent_orgs.append(word)
                    org_index += 1
                elif tag == 'I-ORG' and org_index != -1:
                    sent_orgs[org_index] += f" {word}"
            for org in set(sent_orgs):
                if org not in orgs:
                    orgs[org] = []
                orgs[org].append(sent)

        borrowers, creditors = self.__split_participant_roles(orgs)

        predicted_borrower = max(borrowers.items(), key=lambda k: k[1])[0]
        trimmed_creditors = [kv[0].strip() for kv in sorted(creditors.items(), key=lambda item: item[1], reverse=True)]
        return ParticipantsModel(predicted_borrower.strip(), trimmed_creditors)

    def __count_roles(self, sentences, org):
        borrower_count = 0
        creditor_count = 0
        for sent in sentences:
            borrower_anchor_dist = find_distance(self.__nlp, sent, "заемщик", org)
            creditor_anchor_dist = find_distance(self.__nlp, sent, "кредитор", org)

            if borrower_anchor_dist >= 0 and creditor_anchor_dist >= 0:
                if borrower_anchor_dist <= creditor_anchor_dist:
                    borrower_count += 1
                if borrower_anchor_dist >= creditor_anchor_dist:
                    creditor_count +=1
            elif borrower_anchor_dist >= 0:
                borrower_count += 1
            elif creditor_anchor_dist >= 0:
                creditor_count += 1

        return borrower_count, creditor_count

    def __split_participant_roles(self, orgs):
        borrowers = {}
        creditors = {}
        for org in orgs:
            borrower_count, creditor_count = self.__count_roles(orgs[org], org)
            if borrower_count > creditor_count:
                borrowers[org] = borrower_count
            elif creditor_count > 0:
                creditors[org] = creditor_count
            else:
                print(f"{org} - Неизвестно")
        return borrowers, creditors

    def extract(self, content):
        doc = self.__nlp(content)
        return self.__extract_participants(doc)
