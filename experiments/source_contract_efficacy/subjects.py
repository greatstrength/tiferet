"""Actual Ly subjects and in-memory AST mutants; no assertions or source writes."""

# *** imports

# ** core
import ast
import inspect
import textwrap
from pathlib import Path

# ** infra
import tiferet_ly
from tiferet_ly.events import lex as lex_module
from tiferet_ly.utils import layout as layout_module

# *** constants

# ** constant: ly_root
LY_ROOT = Path(tiferet_ly.__file__).resolve().parent.parent

# *** classes

# ** class: contract_subject
class ContractSubject:
    """Expose unprojected real objects/source, changing only an isolated mutant."""

    # * init
    def __init__(self, mode='baseline'):
        """Create one immutable-source experiment subject.

        :param mode: The isolated mutation to apply.
        :type mode: str
        """

        self.mode = mode
        self._function = lex_module.LexText.execute
        self._profile = layout_module.LayoutProfileView
        self._apply = layout_module.LayoutFilter.apply
        self._filter = layout_module.LayoutFilter
        self._source = Path(layout_module.__file__).read_text()
        if mode.startswith('signature_'):
            original = inspect.unwrap(lex_module.LexText.execute)
            tree = ast.parse(textwrap.dedent(inspect.getsource(original)))
            function = tree.body[0]
            function.decorator_list = []
            if mode == 'signature_order':
                function.args.args[1], function.args.args[2] = function.args.args[2], function.args.args[1]
            elif mode == 'signature_kind':
                function.args.posonlyargs = function.args.args[:3]
                function.args.args = function.args.args[3:]
            elif mode == 'signature_default':
                function.args.defaults[-1] = ast.Constant(False)
            else:
                raise ValueError(mode)
            namespace = dict(vars(lex_module))
            exec(compile(ast.fix_missing_locations(tree), '<isolated-Ly-signature-mutant>', 'exec'), namespace)
            self._function = namespace['execute']
        elif mode in ('annotation_identity', 'protocol_field'):
            tree = ast.parse(self._source)
            if mode == 'protocol_field':
                protocol = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'LayoutProfileView')
                protocol.body = [n for n in protocol.body if not (isinstance(n, ast.AnnAssign) and n.target.id == 'tab_size')]
            else:
                filter_cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'LayoutFilter')
                apply = next(n for n in filter_cls.body if isinstance(n, ast.FunctionDef) and n.name == 'apply')
                next(a for a in apply.args.args if a.arg == 'profile').annotation = ast.Name(id='object', ctx=ast.Load())
            namespace = dict(vars(layout_module))
            exec(compile(ast.fix_missing_locations(tree), '<isolated-Ly-layout-mutant>', 'exec'), namespace)
            self._profile = namespace['LayoutProfileView']
            self._filter = namespace['LayoutFilter']
            self._apply = self._filter.apply
        elif mode != 'baseline':
            additions = {
                'import_absolute': '\nfrom tiferet_ly.domain import LayoutProfile\n',
                'import_relative': '\nfrom ..domain import LayoutProfile\n',
                'import_relative_child': '\nfrom ..domain.layout import LayoutProfile\n',
                'import_alias': '\nimport tiferet_ly.domain as hidden_domain\n',
                'import_from_root': '\nfrom tiferet_ly import domain as hidden_domain\n',
                'comment_only': '\n# Documentation mentions tiferet_ly.domain, without importing it.\n',
                'ast_literal_only': '\nAST_DESCRIPTION = "ImportFrom(module=\'domain\', names=[])"\n',
            }
            self._source += additions[mode]
            ast.parse(self._source)

    # * method: function
    def function(self):
        """Return the actual event callable or its isolated AST-derived mutant."""

        return self._function

    # * method: profile
    def profile(self):
        """Return the actual protocol class, with no normalized assertion rows."""

        return self._profile

    # * method: apply
    def apply(self):
        """Return the actual static callable whose annotation is under test."""

        return self._apply

    # * method: source
    def source(self):
        """Return raw source text, not prefiltered imports or a verdict."""

        return self._source
