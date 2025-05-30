from databases.connections import Settings
from databases.connections import AsyncDatabase
from datetime import datetime,timedelta
from models.model import (
    UserList,
    CloudList,
    ServiceList,
    ThirdPartyList,
    ManagedServiceList,
    OtherServiceList,
    TotalChargeList,
    TotalCloudChargeList,
    TotalChargeThirdPartyList,
    TotalChargeManagedServiceList,
    TotalChargeOtherServiceList,
    ChargeCloudServiceList,
    TypeChargeList,
    ItemChargeList,
    ChargeThirdPartyList,
    ChargeManagedServiceList,
    ChargeOtherServiceList,
)


class ChargeInfoManager:
    def __init__(self):
        self.collection_user_list = AsyncDatabase(UserList)
        self.collection_cloud_list = AsyncDatabase(CloudList)
        self.collection_service_list = AsyncDatabase(ServiceList)
        self.collection_third_party_list = AsyncDatabase(ThirdPartyList)
        self.collection_managed_service_list = AsyncDatabase(ManagedServiceList)
        self.collection_other_service_list = AsyncDatabase(OtherServiceList)
        self.collection_total_charge_list = AsyncDatabase(TotalChargeList)
        self.collection_total_cloud_charge_list = AsyncDatabase(TotalCloudChargeList)
        self.collection_total_third_party_charge_list = AsyncDatabase(TotalChargeThirdPartyList)
        self.collection_total_managed_service_charge_list = AsyncDatabase(TotalChargeManagedServiceList)
        self.collection_total_other_service_charge_list = AsyncDatabase(TotalChargeOtherServiceList)
        self.collection_third_party_charge_list = AsyncDatabase(ChargeThirdPartyList)
        self.collection_managed_service_charge_list = AsyncDatabase(ChargeManagedServiceList)
        self.collection_other_service_charge_list = AsyncDatabase(ChargeOtherServiceList)
        self.collection_service_charge_list = AsyncDatabase(ChargeCloudServiceList)
        self.collection_type_charge_list = AsyncDatabase(TypeChargeList)
        self.collection_item_charge_list = AsyncDatabase(ItemChargeList)
        self.charge_collection_dict = {
            "TOTAL": {
                "TOTAL_CHARGE_COLLECTION": self.collection_total_charge_list,
                "TOTAL_CHARGE_COLLECTION_KEY": "TOTAL_",
                "TOTAL_CHARGE_DB": TotalChargeList,
            },
            "CLOUD": {
                "TOTAL_CHARGE_COLLECTION": self.collection_total_cloud_charge_list,
                "CHARGE_LIST_COLLECTION": self.collection_service_charge_list,
                "TOTAL_CHARGE_COLLECTION_KEY": "TOTAL_CHARGE_CLOUD_",
                "CHARGE_LIST_COLLECTION_KEY": "CLOUD_SERVICE_",
                "TOTAL_CHARGE_DB": TotalCloudChargeList,
                "CHARGE_LIST_DB": ChargeCloudServiceList,
            },
            "CHARGE_THIRD_PARTY": {
                "TOTAL_CHARGE_COLLECTION": self.collection_total_third_party_charge_list,
                "CHARGE_LIST_COLLECTION": self.collection_third_party_charge_list,
                "SERVICE_LIST_COLLECTION": self.collection_third_party_list,
                "TOTAL_CHARGE_COLLECTION_KEY": "TOTAL_CHARGE_THIRD_PARTY_",
                "CHARGE_LIST_COLLECTION_KEY": "CHARGE_THIRD_PARTY_",
                "SERVICE_LIST_COLLECTION_KEY": "THIRD_PARTY_",
                "TOTAL_CHARGE_DB": TotalChargeThirdPartyList,
                "CHARGE_LIST_DB": ChargeThirdPartyList,
                "SERVICE_LIST_DB": ThirdPartyList
            },
            "CHARGE_MANAGED_SERVICE": {
                "TOTAL_CHARGE_COLLECTION": self.collection_total_managed_service_charge_list,
                "CHARGE_LIST_COLLECTION": self.collection_managed_service_charge_list,
                "SERVICE_LIST_COLLECTION": self.collection_managed_service_list,
                "TOTAL_CHARGE_COLLECTION_KEY": "TOTAL_CHARGE_MANAGED_SERVICE_",
                "CHARGE_LIST_COLLECTION_KEY": "CHARGE_MANAGED_SERVICE_",
                "SERVICE_LIST_COLLECTION_KEY": "MANAGED_SERVICE_",
                "TOTAL_CHARGE_DB": TotalChargeManagedServiceList,
                "CHARGE_LIST_DB": ChargeManagedServiceList,
                "SERVICE_LIST_DB": ManagedServiceList
            },
            "CHARGE_OTHER_SERVICE": {
                "TOTAL_CHARGE_COLLECTION": self.collection_total_other_service_charge_list,
                "CHARGE_LIST_COLLECTION": self.collection_other_service_charge_list,
                "SERVICE_LIST_COLLECTION": self.collection_other_service_list,
                "TOTAL_CHARGE_COLLECTION_KEY": "TOTAL_CHARGE_OTHER_SERVICE_",
                "CHARGE_LIST_COLLECTION_KEY": "CHARGE_OTHER_SERVICE_",
                "SERVICE_LIST_COLLECTION_KEY": "OTHER_SERVICE_",
                "TOTAL_CHARGE_DB": TotalChargeOtherServiceList,
                "CHARGE_LIST_DB": ChargeOtherServiceList,
                "SERVICE_LIST_DB": OtherServiceList
            },
            "THIRD_PARTY": {
                "TOTAL_CHARGE_COLLECTION": self.collection_total_third_party_charge_list,
                "CHARGE_LIST_COLLECTION": self.collection_third_party_charge_list,
                "SERVICE_LIST_COLLECTION": self.collection_third_party_list,
                "TOTAL_CHARGE_COLLECTION_KEY": "TOTAL_CHARGE_THIRD_PARTY_",
                "CHARGE_LIST_COLLECTION_KEY": "CHARGE_THIRD_PARTY_",
                "SERVICE_LIST_COLLECTION_KEY": "THIRD_PARTY_",
                "TOTAL_CHARGE_DB": TotalChargeThirdPartyList,
                "CHARGE_LIST_DB": ChargeThirdPartyList,
                "SERVICE_LIST_DB": ThirdPartyList
            },
            "MANAGED_SERVICE": {
                "TOTAL_CHARGE_COLLECTION": self.collection_total_managed_service_charge_list,
                "CHARGE_LIST_COLLECTION": self.collection_managed_service_charge_list,
                "SERVICE_LIST_COLLECTION": self.collection_managed_service_list,
                "TOTAL_CHARGE_COLLECTION_KEY": "TOTAL_CHARGE_MANAGED_SERVICE_",
                "CHARGE_LIST_COLLECTION_KEY": "CHARGE_MANAGED_SERVICE_",
                "SERVICE_LIST_COLLECTION_KEY": "MANAGED_SERVICE_",
                "TOTAL_CHARGE_DB": TotalChargeManagedServiceList,
                "CHARGE_LIST_DB": ChargeManagedServiceList,
                "SERVICE_LIST_DB": ManagedServiceList
            },
            "OTHER_SERVICE": {
                "TOTAL_CHARGE_COLLECTION": self.collection_total_other_service_charge_list,
                "CHARGE_LIST_COLLECTION": self.collection_other_service_charge_list,
                "SERVICE_LIST_COLLECTION": self.collection_other_service_list,
                "TOTAL_CHARGE_COLLECTION_KEY": "TOTAL_CHARGE_OTHER_SERVICE_",
                "CHARGE_LIST_COLLECTION_KEY": "CHARGE_OTHER_SERVICE_",
                "SERVICE_LIST_COLLECTION_KEY": "OTHER_SERVICE_",
                "TOTAL_CHARGE_DB": TotalChargeOtherServiceList,
                "CHARGE_LIST_DB": ChargeOtherServiceList,
                "SERVICE_LIST_DB": OtherServiceList
            },
        }

    @staticmethod
    def charge_info_str(total_charge_info):
        dict_key_list = [i for i in total_charge_info.keys()]
        for dict_key in dict_key_list:
            if "BILL_MONTH" in dict_key and total_charge_info[dict_key] is not None:
                total_charge_info["BILL_MONTH_STR"] = (
                    str(total_charge_info["BILL_MONTH"])[:4]
                    + "년 "
                    + str(total_charge_info["BILL_MONTH"])[4:]
                    + "월"
                )
            elif (
                "AMT" in dict_key
                and total_charge_info[dict_key] is not None
                and "_STR" not in dict_key
            ):
                total_charge_info[dict_key + "_STR"] = (
                    f"{int(total_charge_info[dict_key]):,} 원"
                )
        return total_charge_info

    @staticmethod
    def filter_dict_create(form_list):
        form_list = form_list._list
        category_list = list()
        cloud_list = list()
        condition_dict = {}
        for form_data in form_list:
            if form_data[0] == "customer_name":
                condition_dict["user_name"] = form_data[1]
            elif form_data[0] == "category":
                category_list.append(form_data[1])
            elif form_data[0] == "start_date":
                start_date = int(form_data[1].replace("-", ""))
                condition_dict["start_date"] = start_date
            elif form_data[0] == "end_date":
                end_date = int(form_data[1].replace("-", ""))
                condition_dict["end_date"] = end_date
            elif form_data[0] == "cloud-company":
                cloud_list.append(form_data[1])
        condition_dict["class_list"] = list(category_list)
        condition_dict["cloud_list"] = list(cloud_list)
        return condition_dict

    async def get_user_info_by_cloud_id(self, total_charge_element):
        conditions = {"CLOUD_ID": total_charge_element["CLOUD_ID"]}
        cloud_info = await self.collection_cloud_list.get_by_conditions(conditions)
        conditions = {"USER_ID": cloud_info["USER_ID"]}
        user_info = await self.collection_user_list.get_by_conditions(conditions)

        user_dict = {
            "USER_ID": user_info["USER_ID"],
            "USER_NAME": user_info["USER_NAME"],
            "CLOUD_USER_ID": cloud_info["CLOUD_USER_ID"],
            "CLOUD_USER_NUM": cloud_info["CLOUD_USER_NUM"],
            "CLOUD_CLASS": cloud_info["CLOUD_CLASS"],
            "CLOUD_NAME": cloud_info["CLOUD_NAME"],
        }
        return user_dict

    async def get_cloud_service_charge(self, cloud_service_charge_list):
        for cloud_service_charge_info in cloud_service_charge_list:
            service_charge_id = cloud_service_charge_info["CLOUD_SERVICE_CHARGE_ID"]
            conditions = {"CLOUD_SERVICE_CHARGE_ID": service_charge_id}
            type_charge_list = (
                await self.collection_type_charge_list.gets_by_conditions(conditions)
            )
            type_list = []
            type_charge_length = 1

            for type_charge_info in type_charge_list:
                type_charge_id = type_charge_info["TYPE_CHARGE_ID"]
                conditions = {"TYPE_CHARGE_ID": type_charge_id}

                item_charge_list = (
                    await self.collection_item_charge_list.gets_by_conditions(
                        conditions
                    )
                )
                item_charge_list = [
                    self.charge_info_str(item_info) for item_info in item_charge_list
                ]
                type_charge_info["item_list"] = item_charge_list

                item_charge_length = len(item_charge_list) + 1
                type_charge_length += item_charge_length
                type_charge_info["ITEM_CHARGE_LENGH"] = item_charge_length

                type_charge_info = self.charge_info_str(type_charge_info)
                type_list.append(type_charge_info)

            cloud_service_charge_info["TYPE_CHARGE_LENGH"] = type_charge_length
            cloud_service_charge_info["type_list"] = type_list

            cloud_service_charge_info = self.charge_info_str(cloud_service_charge_info)
        return cloud_service_charge_list

    async def get_user_list(self, user_list, cloud_list_conditions):
        result_list = []
        for user_element in user_list:
            cloud_list_conditions["USER_ID"] = {"eq": user_element["USER_ID"]}
            cloud_list = await self.collection_cloud_list.gets_by_conditions(cloud_list_conditions)
            for cloud_element in cloud_list:
                user_element = {
                    "USER_ID": user_element["USER_ID"],
                    "USER_NAME": user_element["USER_NAME"],
                    "CLOUD_ID": cloud_element["CLOUD_ID"],
                    "CLOUD_CLASS": cloud_element["CLOUD_CLASS"],
                    "CLOUD_NAME": cloud_element["CLOUD_NAME"]
                }
                result_list.append(user_element)
        return result_list

    async def get_user_info(self, CLOUD_ID):
        user_info_conditions = {"CLOUD_ID": {"eq": CLOUD_ID}}
        cloud_list_conditions = {"CLOUD_ID": {"eq": CLOUD_ID}}

        user_info = await self.collection_user_list.get_by_conditions(
            user_info_conditions
        )
        cloud_info = await self.collection_cloud_list.get_by_conditions(
            cloud_list_conditions
        )

        user_dict = {
            "USER_ID": user_info["USER_ID"],
            "USER_NAME": user_info["USER_NAME"],
            "CLOUD_ID": cloud_info['CLOUD_ID'],
            "CLOUD_CLASS": cloud_info['CLOUD_CLASS'],
            "CLOUD_NAME": cloud_info['CLOUD_NAME'],
        }
        return user_dict

    async def get_cloud_info(self,CLOUD_ID):
        cloud_list_conditions = {"CLOUD_ID": {"eq": CLOUD_ID}}
        cloud_info = await self.collection_cloud_list.get_by_conditions(cloud_list_conditions)

        user_info_conditions = {"USER_ID": {"eq": cloud_info['USER_ID']}}
        user_info = await self.collection_user_list.get_by_conditions(user_info_conditions)
        cloud_info['USER_NAME'] = user_info['USER_NAME']

        third_party_list = await self.collection_third_party_list.gets_by_conditions(cloud_list_conditions)
        managed_service_list = await self.collection_managed_service_list.gets_by_conditions(cloud_list_conditions)
        other_service_list = await self.collection_other_service_list.gets_by_conditions(cloud_list_conditions)
        
        third_party_list = [self.charge_info_str(third_party_element) for third_party_element in third_party_list]
        managed_service_list = [self.charge_info_str(managed_service_element) for managed_service_element in managed_service_list]
        other_service_list = [self.charge_info_str(other_service_element) for other_service_element in other_service_list]
        return cloud_info, third_party_list,managed_service_list,other_service_list

    async def get_cloud_charge_list(self, CLOUD_ID, date_range):
        cloud_list_conditions = {"CLOUD_ID": {"eq": CLOUD_ID}}
        cloud_info = await self.collection_cloud_list.get_by_conditions(cloud_list_conditions)

        user_info_conditions = {"USER_ID": {"eq": cloud_info['USER_ID']}}
        user_info = await self.collection_user_list.get_by_conditions(user_info_conditions)

        cloud_info['USER_NAME'] = user_info['USER_NAME']
        
        total_charge_list_conditions = {
            "BILL_MONTH": {"gte": date_range["start_date"],"lte": date_range["end_date"]},
            "CLOUD_ID":{"eq":cloud_info['CLOUD_ID']}
        }
        total_charge_data = await self.collection_total_charge_list.gets_by_conditions(total_charge_list_conditions)


        total_charge_list = []
        for total_charge_element in total_charge_data:
            total_charge_element["USER_NAME"] = cloud_info["USER_NAME"]
            total_charge_element["CLOUD_CLASS"] = cloud_info["CLOUD_CLASS"]
            total_charge_element["CLOUD_NAME"] = cloud_info["CLOUD_NAME"]

            total_charge_element = self.charge_info_str(total_charge_element)
            total_charge_list.append(total_charge_element)


        sorted_charge_list = sorted(total_charge_list, key=lambda x: x["BILL_MONTH"], reverse=True)
        
        return cloud_info,sorted_charge_list

    async def get_billing_list(self, user_list, cloud_list_conditions, date_range):
        total_charge_list = []

        cloud_charge_list_conditions = {
            "BILL_MONTH": {
                "gte": date_range["start_date"],
                "lte": date_range["end_date"],
            }
        }

        for user_info in user_list:
            user_id = user_info["USER_ID"]
            user_name = user_info["USER_NAME"]

            cloud_list_conditions["USER_ID"] = {"eq": user_id}
            cloud_list = await self.collection_cloud_list.gets_by_conditions(
                cloud_list_conditions
            )

            for cloud_info in cloud_list:
                cloud_id = cloud_info["CLOUD_ID"]
                cloud_class = cloud_info["CLOUD_CLASS"]
                cloud_name = cloud_info["CLOUD_NAME"]

                cloud_charge_list_conditions["CLOUD_ID"] = {"eq": cloud_id}
                total_charge_elements = (
                    await self.collection_total_charge_list.gets_by_conditions(
                        cloud_charge_list_conditions
                    )
                )

                for total_charge_info in total_charge_elements:
                    total_charge_info["USER_NAME"] = user_name
                    total_charge_info["CLOUD_CLASS"] = cloud_class
                    total_charge_info["CLOUD_NAME"] = cloud_name

                    total_charge_info = self.charge_info_str(total_charge_info)

                    total_charge_list.append(total_charge_info)

        sorted_charge_list = sorted(
            total_charge_list, key=lambda x: x["BILL_MONTH"], reverse=True
        )
        return sorted_charge_list

    async def update_collection_charge_list(self, service_list, total_charge_id, charge_dict):
        total_charge_collection = charge_dict["TOTAL_CHARGE_COLLECTION"]
        collection_total_charge_id = charge_dict["TOTAL_CHARGE_COLLECTION_KEY"] + "ID"
        charge_list_collection = charge_dict["CHARGE_LIST_COLLECTION"]
        collection_charge_list_id = charge_dict["CHARGE_LIST_COLLECTION_KEY"] + "ID"
        
        model_class = charge_dict["CHARGE_LIST_DB"]
        collection_total_charge_info_conditions = {
            "TOTAL_CHARGE_ID": {"eq": total_charge_id}
        }
        collection_total_charge_info = await total_charge_collection.get_by_conditions(collection_total_charge_info_conditions)
        collection_charge_list_condition = {
            collection_total_charge_id: {
                "eq": collection_total_charge_info[collection_total_charge_id]
            }
        }
        collection_charge_list = await charge_list_collection.gets_by_conditions(
            collection_charge_list_condition
        )
        charge_id_list = []

        for service_key in list(service_list.keys()):
            if "NEW" in service_key:
                service_dict = model_class(**service_list[service_key])
                await charge_list_collection.save(service_dict)
            elif "UPDATE" in service_key:
                service_update_dict = service_list[service_key]
                service_update_dict[collection_charge_list_id] = int(
                    service_update_dict[collection_charge_list_id]
                )
                charge_id_list.append(service_update_dict[collection_charge_list_id])

                await charge_list_collection.update_one(
                    collection_charge_list_id,
                    service_update_dict[collection_charge_list_id],
                    service_update_dict,
                )

        for charge_item in collection_charge_list:
            if charge_item[collection_charge_list_id] not in charge_id_list:
                await charge_list_collection.delete_many(
                    collection_charge_list_id, charge_item[collection_charge_list_id]
                )

    async def update_collection_total_charge_list(self, total_charge_id, charge_dict):
        total_charge_collection = charge_dict["TOTAL_CHARGE_COLLECTION"]
        collection_total_charge_id = (
            charge_dict["TOTAL_CHARGE_COLLECTION_KEY"] + "ID"
        )
        charge_list_collection = charge_dict["CHARGE_LIST_COLLECTION"]
        total_use_amt = charge_dict["TOTAL_CHARGE_COLLECTION_KEY"] + "USE_AMT"
        total_user_pay_amt = charge_dict["TOTAL_CHARGE_COLLECTION_KEY"] + "USER_PAY_AMT"
        collection_use_amt = charge_dict["CHARGE_LIST_COLLECTION_KEY"] + "USE_AMT"
        collection_user_pay_amt = charge_dict["CHARGE_LIST_COLLECTION_KEY"] + "USER_PAY_AMT"
        collection_total_charge_info_conditions = {
            "TOTAL_CHARGE_ID": {"eq": total_charge_id}
        }
        collection_total_charge_info = await total_charge_collection.get_by_conditions(
            collection_total_charge_info_conditions
        )
        collection_charge_list_condition = {
            collection_total_charge_id: {
                "eq": collection_total_charge_info[collection_total_charge_id]
            }
        }
        collection_charge_list = await charge_list_collection.gets_by_conditions(
            collection_charge_list_condition
        )
        collection_charge_list = await charge_list_collection.gets_by_conditions(
            collection_charge_list_condition
        )
        collection_charge_use_sum = sum(
            [
                collection_charge_item[collection_use_amt]
                for collection_charge_item in collection_charge_list
            ]
        )
        collection_charge_user_pay_sum = sum(
            [
                collection_charge_item[collection_user_pay_amt]
                for collection_charge_item in collection_charge_list
            ]
        )
        collection_total_charge_info[total_use_amt] = collection_charge_use_sum
        collection_total_charge_info[total_user_pay_amt] = collection_charge_user_pay_sum
        await total_charge_collection.update_one(
            collection_total_charge_id,
            collection_total_charge_info[collection_total_charge_id],
            collection_total_charge_info
        )


    async def update_collection_list(self, service_list, cloud_id, charge_dict):
        service_list_collection = charge_dict["SERVICE_LIST_COLLECTION"]
        service_list_id = charge_dict['SERVICE_LIST_COLLECTION_KEY']+"ID"
        service_list_condition = {"CLOUD_ID": {"eq": cloud_id}}
        service_list_model = charge_dict["SERVICE_LIST_DB"]
        collection_service_list = await service_list_collection.gets_by_conditions(service_list_condition)

        collection_total_charge_collection = charge_dict["TOTAL_CHARGE_COLLECTION"]
        collection_total_charge_id = (charge_dict["TOTAL_CHARGE_COLLECTION_KEY"] + "ID")

        charge_list_collection = charge_dict["CHARGE_LIST_COLLECTION"]
        collection_charge_list_id = (charge_dict["CHARGE_LIST_COLLECTION_KEY"] + "ID")
        charge_list_model = charge_dict["CHARGE_LIST_DB"]

        service_use_amt = charge_dict["SERVICE_LIST_COLLECTION_KEY"] + "USE_AMT"
        service_user_pay_amt = charge_dict["SERVICE_LIST_COLLECTION_KEY"] + "USER_PAY_AMT"
        collection_use_amt = "CHARGE_" + service_use_amt
        collection_user_pay_amt = "CHARGE_" + service_user_pay_amt
        total_use_amt = "TOTAL_" + collection_use_amt
        total_user_pay_amt = "TOTAL_" + collection_user_pay_amt

        today = datetime.today()
        today_date = int(today.strftime("%Y%m"))
        collection_total_charge_list_conditions = {"CLOUD_ID": {"eq": cloud_id},"BILL_MONTH":{"eq":today_date}}
    
        collection_total_charge_info = await self.collection_total_charge_list.get_by_conditions(collection_total_charge_list_conditions)

        total_charge_id = collection_total_charge_info['TOTAL_CHARGE_ID']
        collection_total_charge_list_condition = {'TOTAL_CHARGE_ID': {"eq": total_charge_id}}
        collection_total_charge_info = await collection_total_charge_collection.get_by_conditions(collection_total_charge_list_condition)
        
        collection_charge_id = collection_total_charge_info[collection_total_charge_id]
        collection_charge_list_condition = {collection_total_charge_id: {"eq": collection_charge_id}}
        collection_charge_list = await charge_list_collection.gets_by_conditions(collection_charge_list_condition)
        
        charge_id_list = []

        for service_key in list(service_list.keys()):
            if "NEW" in service_key:
                service_dict = service_list_model(**service_list[service_key])
                await service_list_collection.save(service_dict)
            elif "UPDATE" in service_key:
                service_update_dict = service_list[service_key]
                service_update_dict[service_list_id] = int(
                    service_update_dict[service_list_id]
                )
                charge_id_list.append(service_update_dict[service_list_id])

                await service_list_collection.update_one(
                    service_list_id,
                    service_update_dict[service_list_id],
                    service_update_dict,
                )

        for charge_item in collection_service_list:
            if charge_item[service_list_id] not in charge_id_list:
                await service_list_collection.delete_one(
                    service_list_id, charge_item[service_list_id]
                )

        await charge_list_collection.delete_many(
                collection_total_charge_id, collection_charge_id
            )

        collection_service_list = await service_list_collection.gets_by_conditions(service_list_condition)
        for collection_service_element in collection_service_list:
            update_collection_dict = {collection_total_charge_id: collection_charge_id,}
            for collection_charge_service_key,collection_charge_service_value in collection_service_element.items():
                if 'ID' not in collection_charge_service_key:
                    service_dict_key = "CHARGE_"+collection_charge_service_key 
                    update_collection_dict[service_dict_key] = collection_charge_service_value
            pass
            service_dict = charge_list_model(**update_collection_dict)
            await charge_list_collection.save(service_dict)
        return total_charge_id


    async def update_total_list(self, update_dict, charge_id):
        update_key_list = [i for i in update_dict.keys()]
        total_charge_info_conditions = {"TOTAL_CHARGE_ID": {"eq": charge_id}}
        total_charge_dict = await self.collection_total_charge_list.get_by_conditions(total_charge_info_conditions)
        total_cloud_charge_dict = await self.collection_total_cloud_charge_list.get_by_conditions(total_charge_info_conditions)
        total_third_party_charge_dict = await self.collection_total_third_party_charge_list.get_by_conditions(total_charge_info_conditions)
        total_managed_service_charge_dict = await self.collection_total_managed_service_charge_list.get_by_conditions(total_charge_info_conditions)
        total_other_service_charge_dict = await self.collection_total_other_service_charge_list.get_by_conditions(total_charge_info_conditions)

        for update_key in update_key_list:
            if "CLOUD" in update_key:
                if "AMT" in update_key and update_dict[update_key]:
                    update_value = int(update_dict[update_key])
                else:
                    update_value = update_dict[update_key]
                total_cloud_charge_dict[update_key] = update_value
            elif "THIRD_PARTY" in update_key:
                if "AMT" in update_key and update_dict[update_key]:
                    update_value = int(update_dict[update_key])
                else:
                    update_value = update_dict[update_key]
                total_third_party_charge_dict[update_key] = update_value
            elif "MANAGED" in update_key:
                if "AMT" in update_key and update_dict[update_key]:
                    update_value = int(update_dict[update_key])
                else:
                    update_value = update_dict[update_key]
                total_managed_service_charge_dict[update_key] = update_value
            elif "OTHER" in update_key:
                if "AMT" in update_key and update_dict[update_key]:
                    update_value = int(update_dict[update_key])
                else:
                    update_value = update_dict[update_key]
                total_other_service_charge_dict[update_key] = update_value
            elif "TOTAL" in update_key:
                if "AMT" in update_key and update_dict[update_key]:
                    update_value = int(update_dict[update_key])
                else:
                    update_value = update_dict[update_key]
                total_charge_dict[update_key] = update_value
        await self.collection_total_charge_list.update_one(
            "TOTAL_CHARGE_ID", charge_id, total_charge_dict
        )
        await self.collection_total_cloud_charge_list.update_one(
            "TOTAL_CHARGE_CLOUD_ID",
            total_cloud_charge_dict["TOTAL_CHARGE_CLOUD_ID"],
            total_cloud_charge_dict,
        )
        await self.collection_total_third_party_charge_list.update_one(
            "TOTAL_CHARGE_THIRD_PARTY_ID",
            total_third_party_charge_dict["TOTAL_CHARGE_THIRD_PARTY_ID"],
            total_third_party_charge_dict,
        )
        await self.collection_total_managed_service_charge_list.update_one(
            "TOTAL_CHARGE_MANAGED_SERVICE_ID",
            total_managed_service_charge_dict["TOTAL_CHARGE_MANAGED_SERVICE_ID"],
            total_managed_service_charge_dict,
        )
        await self.collection_total_other_service_charge_list.update_one(
            "TOTAL_CHARGE_OTHER_SERVICE_ID",
            total_other_service_charge_dict["TOTAL_CHARGE_OTHER_SERVICE_ID"],
            total_other_service_charge_dict,
        )

        pass

    async def total_charge_calculate(self,charge_id):
        total_charge_info_conditions = {"TOTAL_CHARGE_ID": {"eq": charge_id}}
        total_charge_dict = await self.collection_total_charge_list.get_by_conditions(total_charge_info_conditions)
        total_cloud_charge_dict = await self.collection_total_cloud_charge_list.get_by_conditions(total_charge_info_conditions)
        total_third_party_charge_dict = await self.collection_total_third_party_charge_list.get_by_conditions(total_charge_info_conditions)
        total_managed_service_charge_dict = await self.collection_total_managed_service_charge_list.get_by_conditions(total_charge_info_conditions)
        total_other_service_charge_dict = await self.collection_total_other_service_charge_list.get_by_conditions(total_charge_info_conditions)
        total_charge_dict["TOTAL_USE_AMT"] = (
        total_cloud_charge_dict["TOTAL_CLOUD_USE_AMT"]
        + total_third_party_charge_dict["TOTAL_CHARGE_THIRD_PARTY_USE_AMT"]
        + total_managed_service_charge_dict["TOTAL_CHARGE_MANAGED_SERVICE_USE_AMT"]
        + total_other_service_charge_dict["TOTAL_CHARGE_OTHER_SERVICE_USE_AMT"]
        )
        total_charge_dict["TOTAL_PAY_AMT"] = (
        total_cloud_charge_dict["TOTAL_CLOUD_PAY_AMT"]
        + total_third_party_charge_dict["TOTAL_CHARGE_THIRD_PARTY_PAY_AMT"]
        + total_managed_service_charge_dict["TOTAL_CHARGE_MANAGED_SERVICE_PAY_AMT"]
        + total_other_service_charge_dict["TOTAL_CHARGE_OTHER_SERVICE_PAY_AMT"]
        )
        total_charge_dict["TOTAL_USER_PAY_AMT"] = (
        total_cloud_charge_dict["TOTAL_CLOUD_USER_PAY_AMT"]
        + total_third_party_charge_dict["TOTAL_CHARGE_THIRD_PARTY_USER_PAY_AMT"]
        + total_managed_service_charge_dict["TOTAL_CHARGE_MANAGED_SERVICE_USER_PAY_AMT"]
        + total_other_service_charge_dict["TOTAL_CHARGE_OTHER_SERVICE_USER_PAY_AMT"]
        )

        total_charge_dict['TOTAL_DISCOUNT_INCLUDE_AMT'] = total_charge_dict['TOTAL_USER_PAY_AMT'] - total_charge_dict['TOTAL_SALES_DISCOUNT_AMT'] - total_charge_dict['TOTAL_COIN_USE_AMT'] + total_charge_dict['TOTAL_DEFAULT_AMT']
        total_charge_dict['TOTAL_VAT_AMT'] = int(round(total_charge_dict['TOTAL_DISCOUNT_INCLUDE_AMT']/10,0))
        total_charge_dict['TOTAL_VAT_INCLUDE_AMT'] = total_charge_dict['TOTAL_DISCOUNT_INCLUDE_AMT'] + total_charge_dict['TOTAL_VAT_AMT']
        await self.collection_total_charge_list.update_one("TOTAL_CHARGE_ID", charge_id, total_charge_dict)

    async def billing_info_update(self, update_data, collection_id):
        update_data._list
        update_dict = {}
        collection_name = update_data._dict["collection_name"]
        total_charge_id = collection_id
        if collection_name == "TOTAL":
            for form_element in update_data._list:
                if collection_name in form_element[0]:
                    update_dict[form_element[0]] = form_element[1]
            await self.update_total_list(update_dict, collection_id)
            
        elif collection_name == "CLOUD":
            for form_element in update_data._list:
                cloud_charge_id = form_element[0].split('_')[0]
                if 'TYPE_NOTES' in form_element[0]:
                    await self.collection_type_charge_list.update_one("TYPE_CHARGE_ID",cloud_charge_id,{"TYPE_NOTES":form_element[1]})
                    pass
                elif 'CLOUD_SERVICE_NOTES' in form_element[0]:
                    await self.collection_service_charge_list.update_one("CLOUD_SERVICE_CHARGE_ID",cloud_charge_id,{"CLOUD_SERVICE_NOTES":form_element[1]})
                    pass

        elif "CHARGE_" in collection_name:
            for form_element in update_data._list:
                if collection_name in form_element[0]:
                    row_name = "_".join(form_element[0].split("_")[-2:])
                    column_name = "_".join(form_element[0].split("_")[:-2])
                    if row_name not in update_dict.keys():
                        charge_id_key = self.charge_collection_dict[collection_name]["TOTAL_CHARGE_COLLECTION_KEY"] + "ID"
                        update_dict[row_name] = {charge_id_key: total_charge_id}
                    update_dict[row_name][column_name] = form_element[1]
            await self.update_collection_charge_list(update_dict, total_charge_id, self.charge_collection_dict[collection_name])
            await self.update_collection_total_charge_list(total_charge_id, self.charge_collection_dict[collection_name])
        else :
            for form_element in update_data._list:
                if collection_name in form_element[0]:
                    row_name = "_".join(form_element[0].split("_")[-2:])
                    column_name = "_".join(form_element[0].split("_")[:-2])
                    if row_name not in update_dict.keys():
                        update_dict[row_name] = {'CLOUD_ID': collection_id}
                    update_dict[row_name][column_name] = form_element[1]
            total_charge_id = await self.update_collection_list(update_dict, collection_id, self.charge_collection_dict[collection_name])
            await self.update_collection_total_charge_list(total_charge_id, self.charge_collection_dict[collection_name])

        await self.total_charge_calculate(total_charge_id)
        
    async def get_billing_info(self, total_charge_id, charge_class):
        total_charge_conditons = {"TOTAL_CHARGE_ID": {"eq": total_charge_id}}
        collection_total_list = self.charge_collection_dict[charge_class]["TOTAL_CHARGE_COLLECTION"]
        collection_list = self.charge_collection_dict[charge_class]["CHARGE_LIST_COLLECTION"]
        collection_id = self.charge_collection_dict[charge_class]["TOTAL_CHARGE_COLLECTION_KEY"] + "ID"
        total_collection_charge_info = await collection_total_list.get_by_conditions(total_charge_conditons)
        total_collection_charge_conditions = {
            collection_id: {"eq": total_collection_charge_info[collection_id]}
        }

        total_collection_charge_info = self.charge_info_str(total_collection_charge_info)
        collection_charge_list = await collection_list.gets_by_conditions(total_collection_charge_conditions)
        collection_charge_list = [self.charge_info_str(collection_charge_info) for collection_charge_info in collection_charge_list]
        return total_collection_charge_info, collection_charge_list

    async def get_billing_info_dict(self, charge_id):
        cloud_conditions = {"TOTAL_CHARGE_ID": {"eq": charge_id}}
        total_charge_element = await self.collection_total_charge_list.get_by_conditions(cloud_conditions)
        user_dict = await self.get_user_info_by_cloud_id(total_charge_element)
        total_charge_info = self.charge_info_str(total_charge_element)
        total_charge_id = total_charge_info['TOTAL_CHARGE_ID']
        total_cloud_charge_info,cloud_service_charge_list = await self.get_billing_info(total_charge_id,"CLOUD")
        total_third_party_charge_info,third_party_charge_list = await self.get_billing_info(total_charge_id,"CHARGE_THIRD_PARTY")
        total_managed_service_charge_info,managed_service_charge_list = await self.get_billing_info(total_charge_id,"CHARGE_MANAGED_SERVICE")
        total_other_service_charge_info,other_service_charge_list = await self.get_billing_info(total_charge_id,"CHARGE_OTHER_SERVICE")
        cloud_service_charge_list = await self.get_cloud_service_charge(cloud_service_charge_list)
        billing_info_dict =   {
            "user": user_dict,
            "total_charge_info": total_charge_info,
            "total_cloud_charge_info": total_cloud_charge_info,
            "total_third_party_charge_info": total_third_party_charge_info,
            "total_managed_service_charge_info": total_managed_service_charge_info,
            "total_other_service_charge_info": total_other_service_charge_info,
            "cloud_service_charge_list": cloud_service_charge_list,
            "managed_service_charge_list": managed_service_charge_list,
            "third_party_charge_list": third_party_charge_list,
            "other_service_charge_list": other_service_charge_list,
        }
        return billing_info_dict
        