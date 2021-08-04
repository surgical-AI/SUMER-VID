import pickle
def save_data_pkl(all_info, train_split, val_split, path):
    train_idx = int(len(all_info) * train_split)
    val_idx = int(len(all_info) * (val_split + train_split))

    train_file_paths = []
    test_file_paths = []
    val_file_paths = []
    val_labels = []
    train_labels = []
    test_labels = []

    train_num_each = []
    val_num_each = []
    test_num_each = []

    for i in range(train_idx):
        train_num_each.append(len(all_info[i]))
        for j in range(len(all_info[i])):
            train_file_paths.append(all_info[i][j][0])
            train_labels.append(all_info[i][j][1:])

    print('num train files: {}'.format(len(train_file_paths)))

    for i in range(train_idx, val_idx):
        val_num_each.append(len(all_info[i]))
        for j in range(len(all_info[i])):
            val_file_paths.append(all_info[i][j][0])
            val_labels.append(all_info[i][j][1:])

    print('num val files: {}'.format(len(val_file_paths)))

    for i in range(val_idx, len(all_info)):
        test_num_each.append(len(all_info[i]))
        for j in range(len(all_info[i])):
            test_file_paths.append(all_info[i][j][0])
            test_labels.append(all_info[i][j][1:])

    print('num test files: {}'.format(len(test_file_paths)))

    train_val_test_paths_labels = []
    train_val_test_paths_labels.append(train_file_paths)
    train_val_test_paths_labels.append(val_file_paths)
    train_val_test_paths_labels.append(test_file_paths)

    train_val_test_paths_labels.append(train_labels)
    train_val_test_paths_labels.append(val_labels)
    train_val_test_paths_labels.append(test_labels)

    train_val_test_paths_labels.append(train_num_each)
    train_val_test_paths_labels.append(val_num_each)
    train_val_test_paths_labels.append(test_num_each)

    print('size of train set: {}, size of test set: {}, size of val set: {}'
          .format(train_idx, len(all_info)-val_idx, val_idx - train_idx))

    with open(path.format(train_idx, val_idx - train_idx, len(all_info) - val_idx),
              'wb') as f:
        pickle.dump(train_val_test_paths_labels, f)