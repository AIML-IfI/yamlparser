import yamlparser
import os
import tempfile

def test_yaml_file():
    yaml_file = os.path.join(os.path.dirname(__file__), "test_config.yaml")
    namespace = yamlparser.NameSpace(yaml_file)

    assert hasattr(namespace, "name")

def test_yaml_dict():
    namespace = yamlparser.NameSpace(dict(name="Name", nested=dict(email="name@host.domain")))

    # check that all the values are stored correctly and can be indexed and attributed
    assert hasattr(namespace, "name")
    assert namespace.name == "Name"
    assert namespace["name"] == "Name"
    assert isinstance(namespace.nested, yamlparser.NameSpace)
    assert isinstance(namespace["nested"], yamlparser.NameSpace)
    assert namespace.nested.email == "name@host.domain"
    assert namespace["nested"]["email"] == "name@host.domain"


def test_extend():
    yaml_file = os.path.join(os.path.dirname(__file__), "test_config.yaml")
    namespace = yamlparser.NameSpace(yaml_file)

    # tests adding a new value
    assert "new_value" not in namespace.dict()
    namespace.new_value = "New Value"
    assert hasattr(namespace, "new_value")
    assert namespace["new_value"] == "New Value"
    # test the same with indexing
    assert "other" not in namespace.dict()
    namespace["other"] = "Other Value"
    assert hasattr(namespace, "other")
    assert namespace.other == "Other Value"

    # tests adding a new sub-namespace with a value
    assert "sub_namespace" not in namespace.dict()
    namespace.new_subnamespace.name = "New Name"
    assert hasattr(namespace, "new_subnamespace")
    assert isinstance(namespace["new_subnamespace"], yamlparser.NameSpace)
    assert hasattr(namespace["new_subnamespace"], "name")
    assert namespace["new_subnamespace"]["name"] == "New Name"
    # test indexing
    assert "another" not in namespace.dict()
    namespace["another"] = dict(novel=17)
    assert hasattr(namespace, "another")
    assert isinstance(namespace.another, yamlparser.NameSpace)
    assert hasattr(namespace.another, "novel")
    assert namespace.another.novel == 17


def test_io():
    namespace = yamlparser.NameSpace(dict(name="Name", nested=dict(email="name@host.domain")))

    try:
        _,filename = tempfile.mkstemp(".yaml")
        # save to file
        namespace.save(filename)
        # create new namespace from file
        namespace = yamlparser.NameSpace(filename)

    finally:
        os.remove(filename)

    # check that all elements are loaded back correctly
    assert hasattr(namespace, "name")
    assert namespace.name == "Name"
    assert isinstance(namespace.nested, yamlparser.NameSpace)
    assert namespace.nested.email == "name@host.domain"


def test_format():
    namespace = yamlparser.NameSpace(dict(name="Name", nested=dict(email="name@host.domain"), value=1.))

    formatted = namespace.format("{name}, {nested.email}, {value}")
    assert formatted == "Name, name@host.domain, 1.0", formatted


if __name__ == "__main__":
    test_yaml_file()
    test_yaml_dict()
    test_extend()
    test_io()
    test_format()
