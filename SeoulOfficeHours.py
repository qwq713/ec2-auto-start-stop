import boto3
import datetime
from typing import List
from typing import Dict


class SeoulOfficeHours:

    def __init__(self):
        self.ec2_client = boto3.client('ec2')

    def instance_ids(self, filter) -> List[str]:
        """
        describe_instances 의 Response 값을 기반으로 instance_id 정보만을 List형태로 출력한다.
        """
        result = []
        
        resp = self.ec2_client.describe_instances(Filters=filter)
        next_token = resp.get("NextToken", False)
        reservations = resp['Reservations']
        
        for reservation in reservations:
            instances = reservation['Instances']
            for instance in instances:
                result.append(instance['InstanceId'])

        while next_token:
            resp = self.ec2_client.describe_instances(Filters=filter,NextToken=next_token)
            next_token = resp.get("NextToken", False)
            reservations = resp['Reservations']
            for reservation in reservations:
                instances = reservation['Instances']
                for instance in instances:
                    result.append(instance['InstanceId'])
        return result

    def start(self, tgt_tag_filter: List[Dict[str, str]]) -> str:
        """
        SeoulOfficeHours EC2 START
        """

        instance_ids = []
        instance_ids = self.instance_ids(tgt_tag_filter)

        if not instance_ids:
            return "There are no instances to start."

        response=self.ec2_client.start_instances(InstanceIds = instance_ids,
                                                   DryRun = False)
        return "START INSTANCES\n"+"\n".join([instance['InstanceId'] for instance in response['StartingInstances']])

    def stop(self, tgt_tag_filter: List[Dict[str, str]]) -> str:
        """
        SeoulOfficeHours EC2 OFF  ( tgt_tag_filter 정보를 통해 대상을 필터링한다.)
        """
        instance_ids=self.instance_ids(
            self.ec2_client.describe_instances(Filters=tgt_tag_filter))

        if not instance_ids:
            return "There are no instances to stop."

        response=self.ec2_client.stop_instances(InstanceIds = instance_ids,
                                                  DryRun = False)
        return "STOP INSTANCES\n"+"\n".join([instance['InstanceId'] for instance in response['StoppingInstances']])


def lambda_handler(event, context):
    """
    cloudwatch로부터 전달된 event 명을 기반으로
    seoul_office_start 혹은 seoul_office_stop 을 실행한다.
    """
    TAG_KEY: str="Schedule"
    TAG_VAL_DEFAULT: str="SEOUL-OFFICE-HOURS"

    _, event_name=event['resources'][0].split("/")

    if event_name == 'seoul_office_start':
        # start 이벤트는 {"Key":"Schedule" , "Value":"SEOUL_OFFICE_HOURS*"} 태그값으로 대상을 필터링한다.
        tag_filter=[{'Name': 'tag:Schedule',
                       'Values': [TAG_VAL_DEFAULT+'*']}]
        msg: str=SeoulOfficeHours().start(tgt_tag_filter = tag_filter)

    elif event_name == 'seoul_office_stop':
        hours: str=datetime.datetime.now().strftime('%H')
        tag_val: str=TAG_VAL_DEFAULT if hours == "18" else TAG_VAL_DEFAULT + \
            f"-{hours}"

        tag_filter=[{'Name': 'tag:Schedule',
                       'Values': [tag_val]}]
        msg: str=SeoulOfficeHours().stop(tgt_tag_filter = tag_filter)

    else:
        msg="""
        The event name could not be found.
        Please check the event name.
        """
    now_datetime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M-%S')
    print(f"[{now_datetime}]", msg)
