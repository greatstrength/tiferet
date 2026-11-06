"""No-pytest fixtures adapted from Ly230047b feature-reader tests; no production edits."""

# *** imports

# ** core
from pathlib import Path

# ** infra
import yaml
import tiferet_ly
from tiferet_ly.mappers.token import ComplexTokenRuleAggregate
from tiferet_ly.mappers.lexeme import LexemeAggregate

# ** app
from tiferet import App

# *** constants

# ** constant: assets
ASSETS = Path(tiferet_ly.__file__).resolve().parent / 'assets'

# *** functions

# ** function: build_app
def build_app(directory):
    '''
    Wire an App session whose DI points at a directory arith catalogue.

    :param directory: The owned temporary directory.
    :type directory: Path
    :return: The wired app.
    :rtype: App
    '''

    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)

    # Write the arithmetic catalogues.
    tokens_path = directory / 'tokens.yml'
    productions_path = directory / 'productions.yml'
    grammars_path = directory / 'grammars.yml'
    tokens_path.write_text(
        yaml.safe_dump({
            'tokens': [
                {'NUMBER': {
                    'grammar_id': 'arith',
                    'pattern': r'\d+',
                    'action': 't.value = int(t.value)\nreturn t',
                }},
                {'PLUS': {
                    'grammar_id': 'arith',
                    'pattern': r'\+',
                }},
            ],
        }),
        encoding='utf-8',
    )
    productions_path.write_text(
        yaml.safe_dump({
            'production_rules': [
                {'expr': {
                    'grammar_id': 'arith',
                    'spec': 'expr : expr PLUS term',
                    'action': 'p[0] = p[1] + p[3]',
                }},
                {'expr': {
                    'grammar_id': 'arith',
                    'spec': 'expr : term',
                }},
                {'term': {
                    'grammar_id': 'arith',
                    'spec': 'term : NUMBER',
                }},
            ],
        }),
        encoding='utf-8',
    )
    grammars_path.write_text(
        yaml.safe_dump({
            'grammars': {
                'arith': {
                    'parent_ids': [],
                    'start': 'expr',
                },
            },
        }),
        encoding='utf-8',
    )

    # Point DI catalogue paths and the app session at the temporary files.
    di_path = directory / 'di.yml'
    di_path.write_text(
        (ASSETS / 'di.yml').read_text(encoding='utf-8')
        .replace('token_config: tokens.yml', f'token_config: {tokens_path}')
        .replace(
            'production_config: productions.yml',
            f'production_config: {productions_path}',
        )
        .replace('grammar_config: grammars.yml', f'grammar_config: {grammars_path}'),
        encoding='utf-8',
    )
    app_path = directory / 'app.yml'
    app_path.write_text(
        (ASSETS / 'app.yml').read_text(encoding='utf-8')
        .replace(
            'logging_config: tiferet_ly/assets/app.yml',
            f'logging_config: {ASSETS / "app.yml"}',
        )
        .replace(
            'di_config: tiferet_ly/assets/di.yml',
            f'di_config: {di_path}',
        )
        .replace(
            'error_config: tiferet_ly/assets/error.yml',
            f'error_config: {ASSETS / "error.yml"}',
        )
        .replace(
            'feature_config: tiferet_ly/assets/feature.yml',
            f'feature_config: {ASSETS / "feature.yml"}',
        ),
        encoding='utf-8',
    )
    # Absolute fixture paths avoid changing process CWD.

    # Return the wired app.
    return App('tiferet_ly', app_config=str(app_path))

# ** function: number_token
def number_token():
    """Construct the exact paired unknown-grammar test token."""

    return ComplexTokenRuleAggregate(name='NUMBER', grammar_id='arith', pattern=r'\d+', action='t.value = int(t.value)\nreturn t')

# ** function: stream
def stream():
    """Return the original paired parse-feature lexeme sequence."""

    return [
        LexemeAggregate(type='NUMBER', value=1, lineno=1, lexpos=0),
        LexemeAggregate(type='PLUS', value='+', lineno=1, lexpos=1),
        LexemeAggregate(type='NUMBER', value=2, lineno=1, lexpos=2),
    ]
