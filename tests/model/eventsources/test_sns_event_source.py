from mock import Mock
from unittest import TestCase
from samtranslator.model.eventsources.push import SNS


class SnsEventSource(TestCase):

    def setUp(self):
        self.logical_id = 'NotificationsProcessor'

        self.sns_event_source = SNS(self.logical_id)
        self.sns_event_source.Topic = 'arn:aws:sns:MyTopic'

        self.function = Mock()
        self.function.get_runtime_attr = Mock()
        self.function.get_runtime_attr.return_value = 'arn:aws:lambda:mock'

    def test_to_cloudformation_returns_permission_and_subscription_resources(self):
        resources = self.sns_event_source.to_cloudformation(
            function=self.function)
        self.assertEquals(len(resources), 2)
        self.assertEquals(resources[0].resource_type,
                          'AWS::Lambda::Permission')
        self.assertEquals(resources[1].resource_type,
                          'AWS::SNS::Subscription')

        subscription = resources[1]
        self.assertEquals(subscription.TopicArn, 'arn:aws:sns:MyTopic')
        self.assertEquals(subscription.Protocol, 'lambda')
        self.assertEquals(subscription.Endpoint, 'arn:aws:lambda:mock')
        self.assertIsNone(subscription.FilterPolicy)

    def test_to_cloudformation_passes_the_filter_policy(self):
        filterPolicy = {
            'attribute1': ['value1'],
            'attribute2': ['value2', 'value3'],
            'attribute3': {'numeric': ['>=', '100']}
        }
        self.sns_event_source.FilterPolicy = filterPolicy

        resources = self.sns_event_source.to_cloudformation(
            function=self.function)
        self.assertEquals(len(resources), 2)
        self.assertEquals(resources[1].resource_type,
                          'AWS::SNS::Subscription')
        subscription = resources[1]
        self.assertEquals(subscription.FilterPolicy, filterPolicy)

    def test_to_cloudformation_throws_when_no_function(self):
        self.assertRaises(TypeError, self.sns_event_source.to_cloudformation)
