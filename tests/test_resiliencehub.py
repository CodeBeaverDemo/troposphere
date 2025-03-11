import unittest

import pytest
from troposphere.resiliencehub import FailurePolicy, ResiliencyPolicy


class TestResiliencyPolicy(unittest.TestCase):
    def test_ResiliencyPolicy(self):
        ResiliencyPolicy(
            "policy",
            Policy={"Hardware": FailurePolicy(RpoInSecs=10, RtoInSecs=10)},
            PolicyName="foo",
            Tier="MissionCritical",
        ).to_dict()

    def test_invalid_policy_key(self):
        with self.assertRaises(ValueError):
            ResiliencyPolicy(
                "policy",
                Policy={"Foo": FailurePolicy(RpoInSecs=10, RtoInSecs=10)},
                PolicyName="foo",
                Tier="MissionCritical",
            ).to_dict()

    def test_invalid_policy_value(self):
        with self.assertRaises(ValueError):
            ResiliencyPolicy(
                "policy",
                Policy={"Hardware": 10},
                PolicyName="foo",
                Tier="MissionCritical",
            ).to_dict()

    def test_invalid_policy_tier(self):
        with self.assertRaises(ValueError):
            ResiliencyPolicy(
                "policy",
                Policy={"Hardware": FailurePolicy(RpoInSecs=10, RtoInSecs=10)},
                PolicyName="foo",
                Tier="foobar",
            ).to_dict()


    def test_failurepolicy_invalid_rpo_type(self):
        """Test FailurePolicy raises error when RpoInSecs is not an integer.""" 
        with self.assertRaises(ValueError):
            # Passing a string instead of an integer should raise an error.
            FailurePolicy(RpoInSecs="ten", RtoInSecs=10)

    def test_failurepolicy_missing_rto(self):
        """Test FailurePolicy raises an error when RtoInSecs is missing."""
        with self.assertRaises(ValueError):
            FailurePolicy(RpoInSecs=10).to_dict()
    def test_valid_policy_with_tags_and_constraint(self):
        """Test ResiliencyPolicy creates a valid dictionary when optional parameters are provided."""
        policy_dict = ResiliencyPolicy(
            "policy",
            Policy={"Hardware": FailurePolicy(RpoInSecs=20, RtoInSecs=30)},
            PolicyName="test_policy",
            Tier="MissionCritical",
            DataLocationConstraint="us-west-2",
            Tags={"Env": "Dev"},
        ).to_dict()
        # In troposphere, the to_dict() output contains "Type" and "Properties" keys.
        props = policy_dict.get("Properties", {})
        self.assertIn("DataLocationConstraint", props)
        self.assertEqual(props["DataLocationConstraint"], "us-west-2")
        self.assertIn("Tags", props)
        self.assertEqual(props["Tags"], {"Env": "Dev"})
    def test_empty_policy_dict(self):
        """Test ResiliencyPolicy converts an empty Policy dictionary correctly into the Properties structure."""
        policy_dict = ResiliencyPolicy(
            "policy",
            Policy={},
            PolicyName="foo",
            Tier="MissionCritical",
        ).to_dict()
        self.assertIn("Properties", policy_dict)
        self.assertIn("Policy", policy_dict["Properties"])
        self.assertEqual(policy_dict["Properties"]["Policy"], {})
        """Test ResiliencyPolicy raises an error when Policy is provided with a non-dictionary type."""
        with self.assertRaises(ValueError):
            ResiliencyPolicy(
                "policy",
                Policy=[{"Hardware": FailurePolicy(RpoInSecs=10, RtoInSecs=10)}],
                PolicyName="foo",
                Tier="MissionCritical",
            ).to_dict()

    def test_failurepolicy_zero_values(self):
        """Test FailurePolicy accepts zero values and returns the correct dictionary representation."""
        fp = FailurePolicy(RpoInSecs=0, RtoInSecs=0)
        d = fp.to_dict()
        self.assertEqual(d["RpoInSecs"], 0)
        self.assertEqual(d["RtoInSecs"], 0)
    def test_failurepolicy_negative_values(self):
        """Test FailurePolicy accepts negative integer values."""
        fp = FailurePolicy(RpoInSecs=-10, RtoInSecs=-20)
        d = fp.to_dict()
        self.assertEqual(d["RpoInSecs"], -10)
        self.assertEqual(d["RtoInSecs"], -20)

    def test_invalid_tags_type(self):
        """Test ResiliencyPolicy raises an error when Tags is not a dictionary."""
        with self.assertRaises((ValueError, TypeError)):
            ResiliencyPolicy(
                "policy",
                Policy={"Hardware": FailurePolicy(RpoInSecs=10, RtoInSecs=10)},
                PolicyName="foo",
                Tier="MissionCritical",
                Tags=["Env", "Dev"],
            ).to_dict()

    def test_invalid_policyname_type(self):
        """Test ResiliencyPolicy raises an error when PolicyName is not a string."""
        with self.assertRaises((ValueError, TypeError)):
            ResiliencyPolicy(
                "policy",
                Policy={"Hardware": FailurePolicy(RpoInSecs=10, RtoInSecs=10)},
                PolicyName=123,
                Tier="MissionCritical",
            ).to_dict()

    def test_invalid_datalocationconstraint_type(self):
        """Test ResiliencyPolicy raises an error when DataLocationConstraint is not a string."""
        with self.assertRaises((ValueError, TypeError)):
            ResiliencyPolicy(
                "policy",
                Policy={"Hardware": FailurePolicy(RpoInSecs=10, RtoInSecs=10)},
                PolicyName="foo",
                Tier="MissionCritical",
                DataLocationConstraint=123,
            ).to_dict()
if __name__ == "__main__":
    unittest.main()
