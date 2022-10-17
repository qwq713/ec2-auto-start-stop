import boto3
import datetime
from typing import List
from typing import Dict

TAG_KEY: str = "Schedule"
TAG_VAL_DEFAULT: str = "SEOUL-OFFICE-HOURS"


class SeoulOfficeHours:

    def __init__(self):
        self.ec2_client = boto3.client('ec2')

    def instance_ids(self, tgt_tag_filter: List[Dict[str, str]]) -> List[str]:
        """
        tgt_tag_filter 에 전달된 태그값(패턴)에 해당하는 모든 EC2의 id를 반환한다.
        """
        result = []

        resp = self.ec2_client.describe_instances(Filters=tgt_tag_filter)
        next_token = resp.get("NextToken", False)
        reservations = resp['Reservations']

        for reservation in reservations:
            instances = reservation['Instances']
            for instance in instances:
                result.append(instance['InstanceId'])

        while next_token:
            resp = self.ec2_client.describe_instances(Filters=tgt_tag_filter, NextToken=next_token)
            next_token = resp.get("NextToken", False)
            reservations = resp['Reservations']
            for reservation in reservations:
                instances = reservation['Instances']
                for instance in instances:
                    result.append(instance['InstanceId'])
        return result

    def start_ec2(self, tgt_tag_filter: List[Dict[str, str]]) -> str:
        """
        Schedule 태그의 값이 SEOUL-OFFICE-HOURS 로 시작하는 모든 EC2를 start 한다.
        """

        instance_ids = []
        instance_ids = self.instance_ids(tgt_tag_filter)

        if not instance_ids:
            return "There are no instances to start."

        response = self.ec2_client.start_instances(InstanceIds=instance_ids,
                                                   DryRun=False)
        return "START INSTANCES\n" + "\n".join([instance['InstanceId'] for instance in response['StartingInstances']])

    def stop_ec2(self, tgt_tag_filter: List[Dict[str, str]]) -> str:
        """
        tgt_tag_filter에 전달된 Schedule 태그의 값에 해당하는 모든 EC2를 중지한다.
        """
        instance_ids = self.instance_ids(
            self.ec2_client.describe_instances(Filters=tgt_tag_filter))

        if not instance_ids:
            return "There are no instances to stop."

        response = self.ec2_client.stop_instances(InstanceIds=instance_ids,
                                                  DryRun=False)
        return "STOP INSTANCES\n" + "\n".join([instance['InstanceId'] for instance in response['StoppingInstances']])


def lambda_handler(event, context):
    """
    AWS Lambda 의 메인 함수
    -> 즉 AWS lambda 실행 시 def lambda_handler(event,context) 가 호출됨

    event 값에 따라 SeoulOfficeHours 클래스의 start_ec2 혹은 stop_ec2 함수를 실행.
    """

    _, event_name = event['resources'][0].split("/")

    if event_name == 'seoul_office_start':
        tag_filter = [{'Name': 'tag:Schedule',
                       'Values': [TAG_VAL_DEFAULT + '*']}]
        msg: str = SeoulOfficeHours().start_ec2(tgt_tag_filter=tag_filter)

    elif event_name == 'seoul_office_stop':
        hours: str = datetime.datetime.now().strftime('%H')
        tag_val: str = TAG_VAL_DEFAULT if hours == "18" else TAG_VAL_DEFAULT + f"-{hours}"

        tag_filter = [{'Name': 'tag:Schedule',
                       'Values': [tag_val]}]
        msg: str = SeoulOfficeHours().stop_ec2(tgt_tag_filter=tag_filter)

    else:
        msg = """
        The event name could not be found.
        Please check the event name.
        """
    now_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M-%S')
    print(f"[{now_datetime}]", msg)
