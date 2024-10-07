from ...objects.sync import Import

def test_import_new():

    # Create the import.
    _import = Import.new(
        type='core',
        import_module='json',
    )

    # Assert the import is correct.
    assert _import.type == 'core'
    assert _import.import_module == 'json'