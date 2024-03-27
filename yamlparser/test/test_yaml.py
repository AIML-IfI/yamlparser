import yamlparser
import os
import tempfile

def test_yaml_file():
    # test import from explicit file
    yaml_file = os.path.join(os.path.dirname(__file__), "test_config.yaml")
    namespace = yamlparser.NameSpace(yaml_file)
    assert hasattr(namespace, "name")

    # test import from package with full path
    namespace = yamlparser.NameSpace("yamlparser @ test/test_config.yaml")
    assert hasattr(namespace, "name")

    # test import from package with short path
    namespace = yamlparser.NameSpace("yamlparser @ test_config.yaml")
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

    formatted = namespace.format(["{name}", "{nested.email}", "{value}"])
    assert formatted == ["Name", "name@host.domain", "1.0"], formatted

    # add some internal names that shall be formatted
    namespace["my_name"] = "{name}"
    namespace.nested.my_email = "{nested.email}"
    namespace.nested["new_email"] = ["{email}"]

    # assert that these elements do not get formatted automatically
    assert namespace["my_name"] == "{name}"
    assert namespace.nested.my_email == "{nested.email}"
    assert namespace.nested["new_email"] == ["{email}"]

    # now, format all samples
    namespace.format_self()

    # make sure that all elements are formatted correctly
    assert namespace["my_name"] == "Name"
    assert namespace.nested.my_email == "name@host.domain"
    assert namespace.nested["new_email"] == ["name@host.domain"]


def test_freeze():
    namespace = yamlparser.NameSpace(dict(name="Name", nested=dict(email="name@host.domain"), value=1.))
    # freeze the namespace
    namespace.freeze()

    # make sure that you can still access the existing attributes
    _ = namespace.name
    _ = namespace["nested"]["email"]


    # assure that modifying or adding features raises an ValueError exceptions
    try:
        namespace["new_name"] = "New Name"
        raise Exception("This should not happen")
    except AttributeError:
        pass

    try:
        namespace.set("new_name", "New Name")
        raise Exception("This should not happen")
    except AttributeError:
        pass

    try:
        namespace.new_name = "New Name"
        raise Exception("This should not happen")
    except AttributeError:
        pass

    try:
        namespace.name = "New Name"
        raise Exception("This should not happen")
    except AttributeError:
        pass

    try:
        namespace["name"] = "New Name"
        raise Exception("This should not happen")
    except AttributeError:
        pass

    # try to unfreeze
    namespace.unfreeze()
    namespace.new_name = "New Name"


def test_sub_namespace():
    # create a namespace that loads another yaml file
    namespace = yamlparser.NameSpace(dict(
        name="Name",
        nested={"yaml":os.path.join(os.path.dirname(__file__), "test_config.yaml"), "name": "new_name"},
        value=1.
    ))
    namespace.freeze()
    assert hasattr(namespace, "nested")
    assert hasattr(namespace.nested, "name")
    assert namespace.nested.name == "new_name"
    assert hasattr(namespace.nested, "pi")
    assert hasattr(namespace.nested, "nested")
    assert hasattr(namespace.nested.nested, "name")


    namespace = yamlparser.NameSpace(dict(
        name="Name",
        nested={"yaml":"yamlparser@test_config.yaml"},
        value=1.
    ))
    namespace.freeze()
    assert hasattr(namespace, "nested")
    assert hasattr(namespace.nested, "name")
    assert hasattr(namespace.nested, "pi")
    assert hasattr(namespace.nested, "nested")
    assert hasattr(namespace.nested.nested, "name")



if __name__ == "__main__":
    test_yaml_file()
    test_yaml_dict()
    test_extend()
    test_io()
    test_format()
    test_freeze()
    test_sub_namespace()
