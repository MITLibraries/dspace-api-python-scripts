# import csv

# from dsaps.workflows import append_items_to_collection
#
#
# def test_append_items_to_collection(client, aspace_mapping,
#                                     aspace_delimited_csv):
#     items = append_items_to_collection(
#         client, '333.3333', aspace_mapping, aspace_delimited_csv
#         )
#     assert next(items) == 'e5f6'
#     raise

#
# def test_populate_coll(client, json_metadata_delim, input_dir):
#     """Test populate_new_coll function."""
#     items = workflows.populate_coll(client, 'local', input_dir, 'pdf',
#                                     json_metadata_delim, 'True', 'c3d4', {})
#     assert next(items) == 'e5f6'
#
#
# def test_populate_new_coll(client, json_metadata_delim, input_dir):
#     """Test populate_new_coll function."""
#     coll_name = 'Collection Name'
#     items = workflows.populate_new_coll(client, '111.1111', coll_name, 'local',
#                                         input_dir, 'pdf', json_metadata_delim,
#                                         'True', {})
#     assert next(items) == 'e5f6'
#
#
# def test_reconcile_files_and_metadata(input_dir, output_dir):
#     """Test reconcile function."""
#     workflows.reconcile_files_and_metadata('tests/files/metadata_delim.csv',
#                                            output_dir, input_dir, 'pdf')
#     with open(f'{output_dir}updated-metadata_delim.csv') as csvfile2:
#         reader = csv.DictReader(csvfile2)
#         for row in reader:
#             assert row['uri'] == '/repo/0/ao/123'
#             assert row['title'] == 'Test Item'
#             assert row['file_identifier'] == 'test'
#     with open(f'{output_dir}no_metadata.csv') as csvfile3:
#         reader = csv.DictReader(csvfile3)
#         for row in reader:
#             assert row['id'] == 'best_01'
#     with open(f'{output_dir}no_files.csv') as csvfile4:
#         reader = csv.DictReader(csvfile4)
#         for row in reader:
#             assert row['id'] == 'tast'
