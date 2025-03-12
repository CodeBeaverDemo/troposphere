import io
import pytest
import setuptools
setuptools.setup = lambda *args, **kwargs: None
from setup import readme

def test_readme_returns_content(monkeypatch):
    """Test that readme returns correct content from a mocked README.rst."""
    def fake_open(file, mode='r', *args, **kwargs):
        # Ensure that the correct file is being opened
        assert file == 'README.rst'
        return io.StringIO("This is a test README")
    monkeypatch.setattr("builtins.open", fake_open)
    result = readme()
    assert result == "This is a test README"

def test_readme_file_not_found(monkeypatch):
    """Test that readme raises FileNotFoundError when README.rst doesn't exist."""
    def fake_open(file, mode='r', *args, **kwargs):
        raise FileNotFoundError("No such file")
    monkeypatch.setattr("builtins.open", fake_open)
    with pytest.raises(FileNotFoundError):
        readme()
def test_setup_configuration(monkeypatch):
    """Test that setup() in setup.py is called with correct configuration parameters."""
    import io
    import importlib
    # Monkeypatch builtins.open to return a fake README contents.
    def fake_open(file, mode='r', *args, **kwargs):
        assert file == 'README.rst'
        return io.StringIO("Fake README")
    monkeypatch.setattr("builtins.open", fake_open)
    # Prepare a capturing setup to intercept the keyword arguments passed.
    captured_kwargs = {}
    def capturing_setup(*args, **kwargs):
        nonlocal captured_kwargs
        captured_kwargs = kwargs
    monkeypatch.setattr(setuptools, "setup", capturing_setup)
    # Reload the setup module so that the setup() call is executed again.
    import setup as setup_module
    importlib.reload(setup_module)
    # Assert that the configuration parameters match expectations
    assert captured_kwargs.get("name") == "troposphere"
    assert captured_kwargs.get("version") == "2.4.1"
    assert captured_kwargs.get("long_description") == "Fake README"
    assert captured_kwargs.get("author") == "Mark Peek"
    assert captured_kwargs.get("author_email") == "mark@peek.org"
    assert "scripts" in captured_kwargs
    assert "install_requires" in captured_kwargs
def test_setup_full_configuration(monkeypatch):
    """Test that the setup() call in setup.py is configured with all expected parameters."""
    import io
    import importlib
    # Fake the open function to return a specific README content
    def fake_open(file, mode='r', *args, **kwargs):
        assert file == 'README.rst'
        return io.StringIO("Full Test README")
    monkeypatch.setattr("builtins.open", fake_open)
    captured_kwargs = {}
    def capturing_setup(*args, **kwargs):
        nonlocal captured_kwargs
        captured_kwargs = kwargs
    monkeypatch.setattr(setuptools, "setup", capturing_setup)
    import setup as setup_module
    importlib.reload(setup_module)
    # Assert that the configuration contains all expected fields and values
    assert captured_kwargs.get("name") == "troposphere"
    assert captured_kwargs.get("version") == "2.4.1"
    assert captured_kwargs.get("description") == "AWS CloudFormation creation library"
    assert captured_kwargs.get("long_description") == "Full Test README"
    assert captured_kwargs.get("author") == "Mark Peek"
    assert captured_kwargs.get("author_email") == "mark@peek.org"
    assert captured_kwargs.get("url") == "https://github.com/cloudtools/troposphere"
    assert captured_kwargs.get("license") == "New BSD license"
    assert captured_kwargs.get("packages") == ['troposphere', 'troposphere.openstack', 'troposphere.helpers']
    assert captured_kwargs.get("scripts") == ['scripts/cfn', 'scripts/cfn2py']
    assert captured_kwargs.get("install_requires") == ["cfn_flip>=1.0.2"]
    assert captured_kwargs.get("test_suite") == "tests"
    assert captured_kwargs.get("tests_require") == ["awacs"]
    assert captured_kwargs.get("extras_require") == {'policy': ['awacs']}
    assert captured_kwargs.get("use_2to3") is True
def test_readme_empty(monkeypatch):
    """Test that readme returns an empty string when README.rst is empty."""
    def fake_open(file, mode='r', *args, **kwargs):
        assert file == 'README.rst'
        return io.StringIO("")
    monkeypatch.setattr("builtins.open", fake_open)
    from setup import readme
    result = readme()
    assert result == ""

def test_readme_no_read_method(monkeypatch):
    """Test that readme raises an AttributeError when the file object does not have a read method."""
    class FakeFile:
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_value, traceback):
            pass
    def fake_open(file, mode='r', *args, **kwargs):
        assert file == 'README.rst'
        return FakeFile()
    monkeypatch.setattr("builtins.open", fake_open)
    from setup import readme
    with pytest.raises(AttributeError):
        readme()