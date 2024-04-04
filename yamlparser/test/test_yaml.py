import yamlparser
import os
import tempfile
import unittest

class TestYaml(unittest.TestCase):

    def test_load_yaml_from_path(self):
        """test various ways of importing yaml files"""

        # test import from explicit file
        yaml_file = os.path.join(os.path.dirname(__file__), "test_config.yaml")
        namespace_explicit = yamlparser.NameSpace(yaml_file)
        
        # test import from package with full path
        namespace_full = yamlparser.NameSpace("yamlparser @ test/test_config.yaml")

        # test import from package with short path
        namespace_short = yamlparser.NameSpace("yamlparser @ test_config.yaml")

        self.assertEqual(namespace_explicit.dump(), namespace_full.dump())
        self.assertEqual(namespace_explicit.dump(), namespace_short.dump())
        self.assertEqual(namespace_full.dump(), namespace_short.dump())

    def test_load_yaml_attributes(self):
        """test that all attributes and their values are loaded correctly from the yaml file"""

        # import from explicit file
        yaml_file = os.path.join(os.path.dirname(__file__), "test_config.yaml")
        namespace = yamlparser.NameSpace(yaml_file)
        self.assertTrue(hasattr(namespace, "name"))
        self.assertTrue(hasattr(namespace, "int_value"))
        self.assertTrue(hasattr(namespace, "list_value"))
        self.assertTrue(hasattr(namespace, "nested"))
        self.assertTrue(hasattr(namespace.nested, "name"))
        self.assertTrue(hasattr(namespace.nested, "pi"))
        self.assertTrue(hasattr(namespace.nested, "nested"))
        self.assertTrue(hasattr(namespace.nested.sub_nested, "name"))
        self.assertTrue(hasattr(namespace.nested, "another"))
        self.assertTrue(hasattr(namespace.nested.another, "dot"))
        self.assertTrue(hasattr(namespace.nested.another.dot, "attribute"))
        self.assertTrue(hasattr(namespace, "some"))
        self.assertTrue(hasattr(namespace.some, "dot"))
        self.assertTrue(hasattr(namespace.some.dot, "attribute"))
        
        self.assertEqual(namespace.name, "test")
        self.assertEqual(namespace.int_value, 42)
        self.assertEqual(namespace.list_value, [10, 42, 101])
        self.assertEqual(namespace.nested.name, "nested_test")
        self.assertEqual(namespace.nested.pi, 3.14159265)
        self.assertEqual(namespace.nested.sub_nested.name, "subnested")
        self.assertEqual(namespace.nested.another.dot.attribute, 37)
        

    def test_yaml_dict(self):
        """test creating a namespace from a dictionary"""
        # TODO: this test is convoluted and tests too many different things at once, such as indexing methods, creating namespace from dict

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


    def test_sub_namespace_override(self):
        """test loading a subnamespace and overriding values in a sub-namespace"""
        # create a namespace that loads another yaml file
        namespace = yamlparser.NameSpace(dict(
            name="Name",
            nested={
                "yaml":os.path.join(os.path.dirname(__file__), "test_config.yaml"), 
                "name": "new_name",
                "sub_nested.name": "new_sub_name",
            },
            value=1.
        ))
        namespace.freeze()

        # test accessing keys of the sub-namespace
        self.assertTrue(hasattr(namespace, "nested"))
        self.assertTrue(hasattr(namespace.nested, "name"))
        self.assertTrue(hasattr(namespace.nested, "pi"))
        self.assertTrue(hasattr(namespace.nested, "sub_nested"))
        self.assertTrue(hasattr(namespace.nested.sub_nested, "name"))
        self.assertTrue(hasattr(namespace.nested, "another"))
        self.assertTrue(hasattr(namespace.nested.another, "dot"))
        self.assertTrue(hasattr(namespace.nested.another.dot, "attribute"))

        # test that the values are correctly overridden
        self.assertEqual(namespace.nested.name, "new_name")
        self.assertEqual(namespace.nested.sub_nested.name, "new_sub_name")


if __name__ == "__main__":
    unittest.main()