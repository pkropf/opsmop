import os
import importlib
import collections

from opsmop.core.fields import Fields

class Page(object):

    def __init__(self, record, dest_dir):

        self.dest_path = os.path.join(dest_dir, "module_%s.rst" % record.name)
        self.elink = self.example_link(record.name)
        self.tlink = self.type_link(record.name)
        self.record = record

    def sphinx_link(self, link, title, prefix=""):
        return "`%s%s <%s>`_" % (prefix, title, link)

    def example_link(self, name):
        return "https://github.com/vespene-io/opsmop-demo/blob/master/module_docs/%s.py" % (name)

    def type_link(self, name):
        return "https://github.com/vespene-io/opsmop/tree/master/opsmop/types/%s.py" % (name)

    def provider_link(self, name):
        return "https://github.com/vespene-io/opsmop/tree/master/opsmop/providers/%s.py" % (name)

    def footer(self, name, top=False):
        buf = ""
        buf = buf + (name.title() + "\n")
        nlen = len(name)
        if not top:
            buf = buf + "-" * nlen
        else:
            buf = buf + "=" * nlen
        buf = buf + "\n"
        return buf

    def get_fields(self, common=False):
        module = importlib.import_module("opsmop.types.%s" % self.record.name)
        class_name = self.record.name.title()
        cls  = getattr(module, class_name)
        try:
            inst = cls()
        except TypeError:
            # for shortcut Types that take a first argument
            inst = cls('')
        fields = inst.fields().fields
        common_fields = Fields.common_field_spec(self, inst)
        if common:
            return collections.OrderedDict(sorted(common_fields.items()))
        else:
            for (k,v) in common_fields.items():
                del fields[k]
            return collections.OrderedDict(sorted(fields.items()))

    def parameter_table(self, fd, caption):
        fd.write(".. list-table:: %s\n" % caption)
        fd.write("    :header-rows: 1\n\n")
        fd.write("    * - Name\n")
        fd.write("      - Help\n")
        fd.write("      - Kind\n")
        fd.write("      - Default\n")


    def field_row(self, fd, name, v):
        def kind(foo):
            if foo is None:
                return "any"
            else:
                return foo.__name__

        if v.help is not None:
            # internal fields have no help
            fd.write("    * - %s\n" % name)
            fd.write("      - %s\n" % v.help)
            fd.write("      - %s\n" % kind(v.kind))
            fd.write("      - %s\n" % v.default)

    def generate(self):

        record = self.record

        fd = open(self.dest_path, "w")

        fd.write(".. image:: ../opsmop.png\n")
        fd.write("   :alt: OpsMop Logo\n")
        fd.write("\n")
        fd.write(".. THIS FILE IS AUTOMATICALLY GENERATED\n")
        fd.write("..\n ")
        fd.write(".. Please do not send pull requests for this file directly.\n")
        fd.write(".. If you wish to update these examples send a pull request here:\n")
        fd.write("..\n ")
        fd.write(".. %s\n" % self.elink)
        fd.write("..\n")
        fd.write(".. This comment only applies to the module documentation\n")
        fd.write("\n")

        # Slug and title
        fd.write(".. _module_%s:\n\n" % self.record.name)
        fd.write(self.footer(self.record.name.title() + " Module", top=True))

        # Description
        fd.write("\n")
        for line in record.description:
            fd.write("%s\n" % line)
        fd.write("\n")

        # Parameters
        fields = self.get_fields(common=False)
        fd.write("\n")
        fields = self.get_fields(common=False)
        if len(fields.keys()):
            self.parameter_table(fd, 'Module Parameters')
            for (k, v) in fields.items():
                self.field_row(fd, k, v)
            fd.write("\n\n")

        # Common Parameters For All Modules
        fields = self.get_fields(common=True)
        self.parameter_table(fd, 'Common Parameters')
        for (k, v) in fields.items():
            self.field_row(fd, k, v)
        fd.write("\n\n")

        # Examples
        fd.write("\n")
        for e in record.examples:
            msg = "Example: %s" % e.name
            fd.write(self.footer(msg))
            fd.write("\n")
            for line in e.description:
                fd.write("%s\n" % line)

            fd.write("\n.. code-block:: python\n")
            fd.write("\n")
            for line in e.code:
                fd.write("    %s\n" % line)
            fd.write("\n")

        # Links to Type Implementations on GitHub
        fd.write(self.footer("Type Implementations"))
        fd.write("* %s\n" % self.sphinx_link(self.type_link(record.name), record.name, prefix='opsmop.types.'))
        fd.write("\n")

        # Same for Providers
        fd.write(self.footer("Provider Implementations"))
        for p in record.providers:
            p1 = p.replace(".","/")
            fd.write("* %s\n" % self.sphinx_link(self.provider_link(p1), p, prefix='opsmop.providers.'))
        fd.write("\n")

        # if there are related modules, link to them all
        if len(record.related_modules):
            fd.write(self.footer("Related Modules"))
            for m in self.record.related_modules:
                fd.write("* :ref:`module_%s`\n" % m)
            fd.write("\n")

        # Link to other language chapters
        fd.write(self.footer("See Also"))
        fd.write("* :ref:`language`\n")
        fd.write("* :ref:`advanced`\n")
        fd.write("* :ref:`development`\n")
        fd.write("\n")

        # Done!
        fd.close()
        print("written: %s" % self.dest_path)