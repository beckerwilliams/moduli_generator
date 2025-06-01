from unittest import (TestCase, main, mock)

from moduli_assembly.scripts import export_bash_builder


class TestModuliAssemblyScripts(TestCase):

    def test_bash_builder_script(self):
        with mock.patch('export_bash_builder') as mk:
            instance = mk.return_value
            instance.method.return_value = 'a result'
            result = export_bash_builder
            self.assertEqual(result, 'a result')


if __name__ == '__main__':
    main()
