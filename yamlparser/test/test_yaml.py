import yamlparser
import os
import tempfile
import unittest

class TestYaml(unittest.TestCase):

    def test_yaml_file(self):
        # test import from explicit file
        yaml_file = os.path.join(os.path.dirname(__file__), "test_config.yaml")
        namespace = yamlparser.NameSpace(yaml_file)
        assert hasattr(namespace, "name")

        # test import from package with full path
        namespace = yamlparser.NameSpace("yamlparser @ test/test_config.yaml")
        self.assertTrue(hasattr(namespace, "name"))

        # test import from package with short path
        namespace = yamlparser.NameSpace("yamlparser @ test_config.yaml")
        self.assertTrue(hasattr(namespace, "name"))


    def test_yaml_dict(self):
        namespace = yamlparser.NameSpace(dict(name="Name", nested=dict(email="name@host.domain")))

        # check that all the values are stored correctly and can be indexed and attributed
        self.assertTrue(hasattr(namespace, "name"))
        self.assertEqual(namespace.name, "Name")
        self.assertEqual(namespace["name"], "Name")
        self.assertIsInstance(namespace.nested, yamlparser.NameSpace)
        self.assertIsInstance(namespace["nested"], yamlparser.NameSpace)
        self.assertEqual(namespace.nested.email, "name@host.domain")
        self.assertEqual(namespace["nested"]["email"], "name@host.domain")



    def test_extend(self):
        yaml_file = os.path.join(os.path.dirname(__file__), "test_config.yaml")
        namespace = yamlparser.NameSpace(yaml_file)

        # tests adding a new value
        self.assertNotIn("new_value", namespace.dict())
        namespace.new_value = "New Value"
        self.assertTrue(hasattr(namespace, "new_value"))
        self.assertEqual(namespace["new_value"], "New Value")
        # test the same with indexing
        self.assertNotIn("other", namespace.dict())
        namespace["other"] = "Other Value"
        self.assertTrue(hasattr(namespace, "other"))
        self.assertEqual(namespace.other, "Other Value")

        # tests adding a new sub-namespace with a value
        self.assertNotIn("new_subnamespace", namespace.dict())
        namespace.new_subnamespace.name = "New Name"
        self.assertTrue(hasattr(namespace, "new_subnamespace"))
        self.assertIsInstance(namespace["new_subnamespace"], yamlparser.NameSpace)
        self.assertTrue(hasattr(namespace["new_subnamespace"], "name"))
        self.assertEqual(namespace["new_subnamespace"]["name"], "New Name")
        # test indexing
        self.assertNotIn("another", namespace.dict())
        namespace["another"] = dict(novel=17)
        self.assertTrue(hasattr(namespace, "another"))
        self.assertIsInstance(namespace.another, yamlparser.NameSpace)
        self.assertTrue(hasattr(namespace.another, "novel"))
        self.assertEqual(namespace.another.novel, 17)


    def test_io(self):
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
        self.assertTrue(hasattr(namespace, "name"))
        self.assertEqual(namespace.name, "Name")
        self.assertIsInstance(namespace.nested, yamlparser.NameSpace)
        self.assertEqual(namespace.nested.email, "name@host.domain")


    def test_format(self):
        namespace = yamlparser.NameSpace(dict(name="Name", nested=dict(email="name@host.domain"), value=1.))

        formatted = namespace.format("{name}, {nested.email}, {value}")
        self.assertEqual(formatted, "Name, name@host.domain, 1.0")

        formatted = namespace.format(["{name}", "{nested.email}", "{value}"])
        self.assertEqual(formatted, ["Name", "name@host.domain", "1.0"])

        # add some internal names that shall be formatted
        namespace["my_name"] = "{name}"
        namespace.nested.my_email = "{nested.email}"
        namespace.nested["new_email"] = ["{email}"]

        # assert that these elements do not get formatted automatically
        self.assertEqual(namespace["my_name"], "{name}")
        self.assertEqual(namespace.nested.my_email, "{nested.email}")
        self.assertEqual(namespace.nested["new_email"], ["{email}"])

        # now, format all samples
        namespace.format_self()

        # make sure that all elements are formatted correctly
        self.assertEqual(namespace["my_name"], "Name")
        self.assertEqual(namespace.nested.my_email, "name@host.domain")
        self.assertEqual(namespace.nested["new_email"], ["name@host.domain"])


    def test_freeze(self):
        namespace = yamlparser.NameSpace(dict(name="Name", nested=dict(email="name@host.domain"), value=1.))
        # freeze the namespace
        namespace.freeze()

        # make sure that you can still access the existing attributes
        _ = namespace.name
        _ = namespace["nested"]["email"]


        # assure that modifying or adding features raises an ValueError exceptions
        with self.assertRaises(AttributeError):
            namespace.new_name = "New Name"
            namespace.set("new_name", "New Name")
            namespace.name = "New Name"
            namespace["name"] = "New Name"
            
        # try to unfreeze
        namespace.unfreeze()
        namespace.new_name = "New Name"


    def test_sub_namespace(self):
        # create a namespace that loads another yaml file
        namespace = yamlparser.NameSpace(dict(
            name="Name",
            nested={"yaml":os.path.join(os.path.dirname(__file__), "test_config.yaml"), "name": "new_name"},
            value=1.
        ))
        namespace.freeze()
        self.assertEqual(namespace.nested.name, "new_name")
        self.assertTrue(hasattr(namespace, "nested"))
        self.assertTrue(hasattr(namespace.nested, "name"))
        self.assertTrue(hasattr(namespace.nested, "pi"))
        self.assertTrue(hasattr(namespace.nested, "nested"))
        self.assertTrue(hasattr(namespace.nested.nested, "name"))

        namespace = yamlparser.NameSpace(dict(
            name="Name",
            nested={"yaml":"yamlparser@test_config.yaml"},
            value=1.
        ))
        namespace.freeze()
        self.assertTrue(hasattr(namespace, "nested"))
        self.assertTrue(hasattr(namespace.nested, "name"))
        self.assertTrue(hasattr(namespace.nested, "pi"))
        self.assertTrue(hasattr(namespace.nested, "nested"))
        self.assertTrue(hasattr(namespace.nested.nested, "name"))



if __name__ == "__main__":
    unittest.main()