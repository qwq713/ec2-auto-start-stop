import boto3
from pprint import pprint
from datetime import datetime
from typing import Any, List


class SeoulOfficeHoursTagManager:
    def __init__(self) -> None:
        self.ec2_client = boto3.client('ec2')
        self.TAG_KEY: str = "Schedule"
        self.TAG_VAL_DEFAULT: str = "SEOUL-OFFICE-HOURS"
        self.TAG_VAL_EXCEPTION_DEFAULT: str = "EXCEPTION-*"
        self.now_yyyymmdd = datetime.now().strftime("%Y%m%d")

    def update_tags(self, instance_ids: List[str], tag_key: str, tag_value: str = "SEOUL-OFFICE-HOURS") -> Any:
        """
        대상 인스턴스 id 목록을 함수의 파라미터로 전달받아서 태그값을 업데이트한다.
        """
        if not instance_ids:
            return "There are no instances to update."
        to_be_tags = [{"Key": tag_key, "Value": tag_value}]
        response = self.ec2_client.create_tags(
            Resources=instance_ids,
            Tags=to_be_tags
        )
        return response

    def comp_nowdate(self, tag_value: str) -> int:
        """
        현재 태그의 년월일(YYYYMMDD) 부분을 추출하여 현재 날짜와 비교한다.
        현재 날짜보다 이전이거나 같을 경우에는 0을 리턴한다.
        현재 날짜보다 이후일경우 1을 리턴한다.
        """
        exception_yyyymmdd = tag_value[len("EXCEPTION-"):]
        if not exception_yyyymmdd:
            return 0

        try:
            if int(exception_yyyymmdd) < int(self.now_yyyymmdd):
                return 1
        except ValueError as e:
            pprint(e)
            return 0

    def append_tgt_instances(self, tgt_instance_ids, reservations):
        for reservation in reservations:
            instances = reservation['Instances']
            for instance in instances:
                # Schedule Tag값을 가져온다.
                inst_tags = instance.get('Tags', [])
                schedule_tag = [
                    tag for tag in inst_tags if tag['Key'] == self.TAG_KEY]

                # Schedule Tag값이 존재하고 & EXCEPTION 날짜 이후인 EC2의 ID값을 가져온다.
                if schedule_tag and self.comp_nowdate(schedule_tag[0]['Value']):
                    tgt_instance_ids.append(instance["InstanceId"])

    def filter_tgt_instance_ids(self) -> List[str]:
        """
        EC2 목록 중 Schedule 태그값이 EXCEPTION- 으로 시작하는 대상을 가져온다.
        이중 예외기간이 지난 인스턴스의 ID 목록을 리스트 형식으로 리턴한다.
        """

        tgt_instance_ids = []
        tgt_tag_filter = [{"Name": 'tag:'+self.TAG_KEY,
                           "Values": [self.TAG_VAL_EXCEPTION_DEFAULT]}]

        # Schedule 태그값이 EXCEPTION- 으로 시작하는 EC2 목록을 가져온다 by tgt_tag_filter
        reservations = self.ec2_client.describe_instances(
            Filters=tgt_tag_filter)
        next_token = reservations.get('NextToken', False)
        reservations = reservations.get('Reservations', [])
        self.append_tgt_instances(tgt_instance_ids,reservations)

        while next_token:
            reservations = self.ec2_client.describe_instances(Filters=tgt_tag_filter,NextToken = next_token)
            next_token = reservations.get('NextToken', False)
            reservations = reservations.get('Reservations', [])
            self.append_tgt_instances(tgt_instance_ids,reservations)
        return tgt_instance_ids

    def start(self) -> Any:
        """
        파워스케줄링 예외기간이 지난 인스턴스의 ID를 추출하여 다시 대상에 포함되도록 태그값을 업데이트한다.
        """
        tgt_instance_ids = self.filter_tgt_instance_ids()
        response = self.update_tags(instance_ids=tgt_instance_ids,
                                    tag_key=self.TAG_KEY, tag_value=self.TAG_VAL_DEFAULT)
        return response


def lambda_handler(event, context):
    seoul_office_hours_tag_mgr = SeoulOfficeHoursTagManager()
    response = seoul_office_hours_tag_mgr.start()
    pprint(f"START DATE : {seoul_office_hours_tag_mgr.now_yyyymmdd}")
    pprint(f"{response}")
