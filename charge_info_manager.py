from databases.connections import Settings
from databases.connections import AsyncDatabase
from models.model import (
    UserList,
    CloudList,
    ServiceList,
    CloudTotalChargeList,
    ServiceChargeList,
    TypeChargeList,
    ItemChargeList,
    ThirdPartyChargeList,
    ManagedServiceList,
    OtherServiceList,
)


class ChargeInfoManager:
    def __init__(self):
        self.collection_user_list = AsyncDatabase(UserList)
        self.collection_cloud_list = AsyncDatabase(CloudList)
        self.collection_service_list = AsyncDatabase(ServiceList)
        self.collection_cloud_total_charge_list = AsyncDatabase(CloudTotalChargeList)
        self.collection_third_party_charge_list = AsyncDatabase(ThirdPartyChargeList)
        self.collection_managed_service_charge_list = AsyncDatabase(ManagedServiceList)
        self.collection_other_service_charge_list = AsyncDatabase(OtherServiceList)
        self.collection_service_charge_list = AsyncDatabase(ServiceChargeList)
        self.collection_type_charge_list = AsyncDatabase(TypeChargeList)
        self.collection_item_charge_list = AsyncDatabase(ItemChargeList)

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
            elif "AMT" in dict_key and total_charge_info[dict_key] is not None:
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

    async def get_user_info_by_user_id(self, user_id):
        conditions = {"USER_ID": user_id}
        user_info = await self.collection_user_list.get_by_conditions(conditions)
        cloud_list = await self.collection_cloud_list.gets_by_conditions(conditions)
        user_detail = {
            "USER_ID": user_info["USER_ID"],
            "USER_NAME": user_info["USER_NAME"],
            "CLOUD_ID": [i["CLOUD_ID"] for i in cloud_list],
            "CLOUD_CLASS": [i["CLOUD_CLASS"] for i in cloud_list],
            "CLOUD_NAME": [i["CLOUD_NAME"] for i in cloud_list],
        }
        return user_detail

    async def get_user_info_by_cloud_id(self, total_charge_element):
        conditions = {"CLOUD_ID": total_charge_element["CLOUD_ID"]}
        cloud_info = await self.collection_cloud_list.get_by_conditions(conditions)
        conditions = {"USER_ID": cloud_info["USER_ID"]}
        user_info = await self.collection_user_list.get_by_conditions(conditions)

        user_dict = {
            "USER_ID": user_info["USER_ID"],
            "USER_NAME": user_info["USER_NAME"],
            "CLOUD_CLASS": cloud_info["CLOUD_CLASS"],
            "CLOUD_NAME": cloud_info["CLOUD_NAME"],
        }
        return user_dict

    async def get_cloud_service_charge(self, cloud_service_charge_list):
        for cloud_service_charge_info in cloud_service_charge_list:
            service_charge_id = cloud_service_charge_info["CLOUD_SERVICE_CHARGE_ID"]
            conditions = {"CLOUD_SERVICE_CHARGE_ID": service_charge_id}
            type_charge_list = await self.collection_type_charge_list.gets_by_conditions(
                conditions
            )
            type_list = []
            type_charge_length = 1
            for type_charge_info in type_charge_list:
                type_charge_id = type_charge_info["TYPE_CHARGE_ID"]

                conditions = {"TYPE_CHARGE_ID": type_charge_id}
                item_charge_list = await self.collection_item_charge_list.gets_by_conditions(
                    conditions
                )
                item_charge_list = [self.charge_info_str(item_info) for item_info in item_charge_list]
                type_charge_info["item_list"] = item_charge_list
                item_charge_length = len(item_charge_list) + 1
                type_charge_info["ITEM_CHARGE_LENGH"] = item_charge_length
                type_charge_length += item_charge_length
                type_charge_info = self.charge_info_str(type_charge_info)
                type_list.append(type_charge_info)
            cloud_service_charge_info["TYPE_CHARGE_LENGH"] = type_charge_length
            cloud_service_charge_info["type_list"] = type_list
            cloud_service_charge_info = self.charge_info_str(cloud_service_charge_info)
        return cloud_service_charge_list
