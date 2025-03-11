import unittest

from troposphere import Template
from troposphere.opsworks import Stack
from troposphere.opsworks import App, Instance, Layer, BlockDeviceMapping, EbsBlockDevice, SslConfiguration


class TestOpsWorksStack(unittest.TestCase):
    def test_nosubnet(self):
        stack = Stack(
            "mystack",
            VpcId="myvpcid",
        )
        with self.assertRaises(ValueError):
            stack.validate()

    def test_stack(self):
        stack = Stack(
            "mystack",
            VpcId="myvpcid",
            DefaultSubnetId="subnetid",
        )
        self.assertIsNone(stack.validate())

    def test_no_required(self):
        stack = Stack(
            "mystack",
        )
        t = Template()
        t.add_resource(stack)
        with self.assertRaises(ValueError):
            t.to_json()

    def test_required(self):
        stack = Stack(
            "mystack",
            DefaultInstanceProfileArn="instancearn",
            Name="myopsworksname",
            ServiceRoleArn="arn",
        )
        t = Template()
        t.add_resource(stack)
        t.to_json()

    def test_custom_json(self):
        stack = Stack(
            "mystack",
            DefaultInstanceProfileArn="instancearn",
            Name="myopsworksname",
            ServiceRoleArn="arn",
        )

        # Test dict works
        t = Template()
        stack.CustomJson = {"foo": "bar"}
        t.add_resource(stack)
        t.to_json()

        # Test json string works
        t = Template()
        stack.CustomJson = '{"foo": "bar"}'
        t.add_resource(stack)
        t.to_json()

        # Test boolean fails
        with self.assertRaises(TypeError):
            stack.CustomJson = True


    def test_app_minimal(self):
        """Test that a minimal valid App resource converts to JSON successfully."""
        app = App(
            "myapp",
            Name="TestApp",
            StackId="stack123",
            Type="other",
        )
        t = Template()
        t.add_resource(app)
        json_output = t.to_json()
        self.assertIn("TestApp", json_output)

    def test_instance_minimal(self):
        """Test that a minimal valid Instance resource converts to JSON successfully."""
        instance = Instance(
            "myinstance",
            InstanceType="t2.micro",
            LayerIds=["layer1"],
            StackId="stack123",
        )
        t = Template()
        t.add_resource(instance)
        json_output = t.to_json()
        self.assertIn("t2.micro", json_output)

    def test_layer_minimal(self):
        """Test that a minimal valid Layer resource converts to JSON successfully."""
        layer = Layer(
            "mylayer",
            AutoAssignElasticIps=True,
            AutoAssignPublicIps=True,
            EnableAutoHealing=True,
            Name="TestLayer",
            Shortname="tlayer",
            StackId="stack123",
            Type="custom",
        )
        t = Template()
        t.add_resource(layer)
        json_output = t.to_json()
        self.assertIn("TestLayer", json_output)

    def test_block_device_mapping(self):
        """Test that BlockDeviceMapping validation does not raise for valid configuration."""
        ebs = EbsBlockDevice(
            DeleteOnTermination=True,
            Iops=100,
            VolumeSize=30,
            VolumeType="gp2",
        )
        mapping = BlockDeviceMapping(
            DeviceName="/dev/sdh",
            Ebs=ebs,
        )
        # This should not raise any exception.
        mapping.validate()

    def test_ssl_configuration_in_app(self):
        """Test that an App with SslConfiguration converts to JSON successfully."""
        ssl_config = SslConfiguration(
            Certificate="cert-data",
            PrivateKey="key-data",
            Chain="chain-data",
        )
        app = App(
            "myappssl",
            Name="SecureApp",
            StackId="stack123",
            Type="php",
            SslConfiguration=ssl_config,
        )
        t = Template()
        t.add_resource(app)
        json_output = t.to_json()
        self.assertIn("SecureApp", json_output)
        self.assertIn("cert-data", json_output)
if __name__ == "__main__":
    unittest.main()
