import pytest
from troposphere.resourcegroups import Group, ResourceQuery, Query, TagFilter, ConfigurationItem, ConfigurationParameter
from troposphere import Tags

class TestResourceGroups:
    """Tests for the resource groups module of troposphere."""

    def test_group_minimum(self):
        """Test creating a Group with only the required 'Name' property."""
        group = Group("TestGroupTitle", Name="TestGroup")
        # Accessing group properties; AWSObject is expected to store properties in 'properties'
        props = getattr(group, "properties", {})
        assert props.get("Name") == "TestGroup"
        # Optional properties should not be set if not provided
        for key in ["Configuration", "Description", "ResourceQuery", "Resources", "Tags"]:
            assert key not in props

    def test_group_full(self):
        """Test creating a Group with all properties including nested configuration."""
        config_param = ConfigurationParameter(Name="Param1", Values=["value1", "value2"])
        config_item = ConfigurationItem(Parameters=[config_param], Type="CustomType")
        tag_filter = TagFilter(Key="Env", Values=["Prod", "Dev"])
        query = Query(ResourceTypeFilters=["AWS::EC2::Instance"], StackIdentifier="stack-123", TagFilters=[tag_filter])
        resource_query = ResourceQuery(Query=query, Type="TAG_FILTERS_1_0")
        group = Group("FullGroupTitle",
            Name="FullGroup",
            Configuration=[config_item],
            Description="A fully configured group",
            ResourceQuery=resource_query,
            Resources=["resource1", "resource2"],
            Tags=Tags({"Key1": "Value1", "Key2": "Value2"})
        )
        props = getattr(group, "properties", {})
        assert props.get("Name") == "FullGroup"
        assert props.get("Description") == "A fully configured group"
        assert isinstance(props.get("Configuration"), list)
        # Check nested configuration parameter structure
        config = props["Configuration"][0]
        assert config.properties.get("Type") == "CustomType"
        parameters = config.properties.get("Parameters", [])
        assert isinstance(parameters, list)
        param = parameters[0]
        assert param.properties.get("Name") == "Param1"
        assert param.properties.get("Values") == ["value1", "value2"]

    def test_resource_query(self):
        """Test creating a ResourceQuery with a Query containing TagFilters."""
        tag_filter1 = TagFilter(Key="Owner", Values=["Alice"])
        tag_filter2 = TagFilter(Key="Status", Values=["Active", "Pending"])
        query = Query(ResourceTypeFilters=["AWS::S3::Bucket"], TagFilters=[tag_filter1, tag_filter2])
        resource_query = ResourceQuery(Query=query, Type="TAG_FILTERS_1_0")
        rq_props = getattr(resource_query, "properties", {})
        query_instance = rq_props.get("Query")
        query_props = getattr(query_instance, "properties", {})
        assert query_props.get("ResourceTypeFilters") == ["AWS::S3::Bucket"]
        tag_filters = query_props.get("TagFilters", [])
        assert len(tag_filters) == 2
        # Validate TagFilter entries using properties dict
        assert tag_filters[0].properties.get("Key") == "Owner"
        assert tag_filters[0].properties.get("Values") == ["Alice"]
        assert tag_filters[1].properties.get("Key") == "Status"
        assert tag_filters[1].properties.get("Values") == ["Active", "Pending"]
        # Also validate that Type is set correctly in ResourceQuery
        assert rq_props.get("Type") == "TAG_FILTERS_1_0"

    def test_missing_required_property(self):
        """Test that missing required property 'Name' in Group raises an error if validated."""
        with pytest.raises(Exception):
            # If the AWSObject validates required properties during instantiation,
            # missing the required 'Name' should raise an exception.
            Group()

    def test_invalid_property_type(self):
        """Test providing an invalid type for a property raises an error."""
        with pytest.raises(Exception):
            # Passing an integer for 'Name' is invalid; expecting an exception during validation.
            Group("InvalidTitle", Name=123)
    def test_empty_optional_properties(self):
        """Test that providing empty lists/dict for optional properties sets the properties accordingly."""
        group = Group("EmptyGroupTitle", Name="EmptyGroup", Configuration=[], Resources=[], Tags=Tags({}))
        props = getattr(group, "properties", {})
        # Check that these properties are set exactly as provided.
        assert props.get("Configuration") == []
        assert props.get("Resources") == []
        tags_obj = props.get("Tags")
        assert isinstance(tags_obj, Tags)
        # Instead of converting to dict, check the underlying tags attribute
        assert hasattr(tags_obj, "tags"), "Tags object should have a 'tags' attribute"
        assert tags_obj.tags == [], "Expected tags attribute to be an empty list"

    def test_invalid_configuration_parameter(self):
        """Test that providing an invalid type for ConfigurationParameter.Values raises an error."""
        with pytest.raises(Exception):
            # Values is expected to be a list of strings; providing an integer in the list should trigger a validation error.
            ConfigurationParameter(Name="InvalidParam", Values=["valid", 100])

    def test_query_with_empty_tag_filters(self):
        """Test that providing an empty list for TagFilters in Query sets the property correctly."""
        query = Query(ResourceTypeFilters=["AWS::Lambda::Function"], TagFilters=[])
        query_props = getattr(query, "properties", {})
        assert query_props.get("TagFilters") == []
        # Validate that when the query is used within ResourceQuery the empty TagFilters are maintained.
        resource_query = ResourceQuery(Query=query, Type="TAG_FILTERS_1_0")
        rq_props = getattr(resource_query, "properties", {})
        query_obj = rq_props.get("Query")
        query_obj_props = getattr(query_obj, "properties", {})
        assert query_obj_props.get("TagFilters") == []
    def test_configuration_item_empty_parameters(self):
        """Test creating a ConfigurationItem with no Parameters specified."""
        # Create ConfigurationItem with only the required Type value
        config_item = ConfigurationItem(Type="EmptyType")
        props = getattr(config_item, "properties", {})
        # Optional Parameters should not be set if not provided
        assert "Parameters" not in props

    def test_query_with_missing_optional(self):
        """Test that a Query defined only with ResourceTypeFilters omits the other optional properties."""
        query = Query(ResourceTypeFilters=["AWS::Lambda::Function"])
        props = getattr(query, "properties", {})
        assert props.get("ResourceTypeFilters") == ["AWS::Lambda::Function"]
        assert "StackIdentifier" not in props
        assert "TagFilters" not in props

    def test_tag_filter_optional(self):
        """Test creating a TagFilter without providing Key or Values results in an empty properties dict."""
        tag_filter = TagFilter()
        props = getattr(tag_filter, "properties", {})
        assert "Key" not in props
        assert "Values" not in props

    def test_invalid_resource_query_type(self):
        """Test that providing an invalid type for ResourceQuery raises an error."""
        with pytest.raises(Exception):
            query = Query(ResourceTypeFilters=["AWS::DynamoDB::Table"])
            # "INVALID_TYPE" should trigger a validation error via resourcequery_type
            ResourceQuery(Query=query, Type="INVALID_TYPE")

    def test_minimal_resource_query(self):
        """Test creating a minimal ResourceQuery with an empty Query property."""
        resource_query = ResourceQuery(Query=Query(), Type="TAG_FILTERS_1_0")
        props = getattr(resource_query, "properties", {})
        query_obj = props.get("Query")
        query_props = getattr(query_obj, "properties", {}) if query_obj else {}
        # All optional properties in Query should not be set
        assert "ResourceTypeFilters" not in query_props
        assert "StackIdentifier" not in query_props
        assert "TagFilters" not in query_props
        # Verify that the ResourceQuery "Type" property is set correctly
        assert props.get("Type") == "TAG_FILTERS_1_0"
    def test_invalid_query_resource_type_filters(self):
        """Test that providing a non-string element in ResourceTypeFilters raises an error."""
        with pytest.raises(Exception):
            # ResourceTypeFilters should be a list of strings
            Query(ResourceTypeFilters=[123])

    def test_invalid_tagfilter_wrong_type(self):
        """Test that providing a non-string for TagFilter Key raises an error."""
        with pytest.raises(Exception):
            # TagFilter Key is expected to be a string
            TagFilter(Key=123, Values=["valid"])

    def test_group_invalid_resources_item(self):
        """Test that providing a non-string element in Resources list raises an error."""
        with pytest.raises(Exception):
            # Each resource in Resources should be a string
            Group("InvalidResourcesTitle", Name="InvalidResources", Resources=[{"not": "a string"}])

    def test_configuration_item_invalid_parameters_content(self):
        """Test that providing an invalid element in ConfigurationItem.Parameters (not a ConfigurationParameter) raises an error."""
        with pytest.raises(Exception):
            # Parameters should be a list of ConfigurationParameter objects
            ConfigurationItem(Parameters=["invalid parameter"], Type="SomeType")