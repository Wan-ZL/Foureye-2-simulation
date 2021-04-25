import numpy as np
import matplotlib.pyplot as plt
from sklearn import neighbors
from sklearn.metrics import mean_squared_error
import pickle
import os
import collections
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from sklearn.metrics import mean_absolute_error
from sklearn.multioutput import MultiOutputRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.linear_model import LinearRegression
from sklearn import svm
# import keras
# from keras.models import Sequential
# from keras.layers import Dense, Dropout, LSTM


def generate_trained_ML(schemes, window_size, n_neighbors, strategy_number):
    for schemes_index in range(len(schemes)):
        all_dataset_X = np.zeros((1, strategy_number))
        all_dataset_Y = np.zeros((1, strategy_number))
        path = "data/trainning_data/" + schemes[schemes_index]
        file_list = [f for f in os.listdir(path) if not f.startswith('.')]
        if len(file_list) == 0:
            print("!! "+schemes[schemes_index]+" No File")
            continue
        for file_name in file_list:
            print("data/trainning_data/" + schemes[schemes_index] + "/"+file_name)
            the_file = open("data/trainning_data/" + schemes[schemes_index] + "/"+file_name, "rb")
            all_result_after_each_game_all_result = pickle.load(the_file)
            the_file.close()


            for key in all_result_after_each_game_all_result.keys():
                # transfer c to S
                # S = np.array(np.sum(all_result_after_each_game_all_result[key], axis=1))
                S = np.array(all_result_after_each_game_all_result[key])

                # padding: [0....0]*window_size to head
                S_with_zero_head = np.concatenate((np.zeros((window_size,strategy_number)), S), axis=0)

                # concatenate to dataset
                all_dataset_X = np.concatenate((all_dataset_X, S_with_zero_head[:-1]), axis=0)
                all_dataset_Y = np.concatenate((all_dataset_Y, S_with_zero_head[1:]), axis=0)


        # !!!================ below estimate each strategy seperately ================
        all_dataset_X_normalized = array_normalization(all_dataset_X)
        all_dataset_Y_normalized = array_normalization(all_dataset_Y)

        model_list = []
        total_R2_predict = 0
        total_R2_no_predict = 0
        total_MSE_predict = 0
        total_MSE_no_predict = 0
        for index in range(strategy_number):
            # strate_dataset_X = all_dataset_X_normalized[:,index].reshape(-1, 1)
            # strate_dataset_Y = all_dataset_Y_normalized[:, index]
            strate_dataset_X = all_dataset_X_normalized[:, index]
            strate_dataset_Y = all_dataset_Y_normalized[:, index]

            # window_size = 5
            # strate_dataset_section_X = np.array([[[strate_dataset_X[i+j]] for i in range(window_size)] for j in range(strate_dataset_X.shape[0]-window_size)])
            strate_dataset_section_X = np.array([[strate_dataset_X[i + j] for i in range(window_size)] for j in
                                                 range(strate_dataset_X.shape[0] - window_size)])
            strate_dataset_section_Y = strate_dataset_Y[window_size:]


            X_train, X_test, y_train, y_test = train_test_split(strate_dataset_section_X, strate_dataset_section_Y, test_size=0.1, random_state=1)

            # KNN
            # n_neighbors = 60
            model = neighbors.KNeighborsRegressor(n_neighbors, weights='distance', algorithm='brute').fit(X_train, y_train)
            # model = svm.SVR().fit(X_train, y_train)
            model_list.append(model)



            # LSTM
            # model = Sequential()
            # model.add(LSTM((1), batch_input_shape=(None,window_size,1), return_sequences=False))
            # model.compile(loss='mean_squared_error',optimizer='adam',metrics=['accuracy'])
            # model.summary()
            # history = model.fit(X_train, y_train, epochs=50, validation_data=(X_test, y_test), verbose=0)


            # print(f"predict {model.score(X_test, y_test)}")
            # print(X_test)
            y_predict = model.predict(X_test)
            # print(f"\nstrategy {index}")
            # print("r2_score")
            # print(f"predict {r2_score(y_test, y_predict)}")
            total_R2_predict += r2_score(y_test, y_predict)
            # print(f"no predict {r2_score(y_test, X_test[:,-1])}")
            total_R2_no_predict += r2_score(y_test, X_test[:,-1])

            # print("Mean Square Error")
            # print(f"predict {mean_squared_error(y_test, y_predict)}")
            total_MSE_predict += mean_squared_error(y_test, y_predict)
            # print(f"no predict {mean_squared_error(y_test, X_test[:,-1])}")
            total_MSE_no_predict += mean_squared_error(y_test, X_test[:,-1])

        print(strate_dataset_section_X.shape)
        print("\n total R2 score")
        print(f"predict {total_R2_predict}")
        print(f"no predict {total_R2_no_predict}")
        print("total MSE")
        print(f"predict {total_MSE_predict}")
        print(f"predict {total_MSE_no_predict}")





        # print(all_dataset_X.shape[0])
        # window_size = 3
        # section_dataset_X = np.array([[all_dataset_X[i+j] for i in range(window_size)] for j in range(all_dataset_X.shape[0]-window_size)])
        # print(section_dataset_X)
        # print(section_dataset_X.shape)
        # print(all_dataset_Y.shape)
        # print(all_dataset_Y[window_size:].shape)
        # n_neighbors = 5
        # knn = neighbors.KNeighborsRegressor(n_neighbors, weights='distance', algorithm='brute')
        # model = knn.fit(section_dataset_X, all_dataset_Y[window_size:])
        # ================ above estimate each strategy separately ================




        # save trained model
        os.makedirs("data/trained_ML_model_list", exist_ok=True)
        the_file = open("data/trained_ML_model_list/knn_trained_model_"+schemes[schemes_index]+".pkl", "wb+")
        pickle.dump(model_list, the_file)
        the_file.close()


def array_normalization(_2d_array):
    sum_array = np.ones((len(_2d_array),strategy_number))/strategy_number
    for index in range(len(_2d_array)):
        if sum(_2d_array[index]) == 0:
            continue
        else:
            sum_array[index] = _2d_array[index]/sum(_2d_array[index])

    # for array in _2d_array:
    #     if sum(array) == 0:
    #         sum_array = np.append(sum_array, 0)
    #     else:
    #         sum_array = np.append(sum_array, sum(array))
    return sum_array



def display_prediction_result(schemes, strategy_number):
    figure_high = 6
    figure_width = 7.5

    for schemes_index in range(len(schemes)):
        print(schemes[schemes_index])
        all_dataset_X = np.zeros((1, strategy_number))
        all_dataset_Y = np.zeros((1, strategy_number))
        path = "data/trainning_data/" + schemes[schemes_index]
        file_list = [f for f in os.listdir(path) if not f.startswith('.')]
        if len(file_list) == 0:
            print("!! " + schemes[schemes_index] + " No File")
            continue
        file_name = file_list[0]
        the_file = open("data/trainning_data/" + schemes[schemes_index] + "/" + file_name, "rb")
        all_result_after_each_game_all_result = pickle.load(the_file)
        the_file.close()

        the_file = open("data/trained_ML_model_LIST/knn_trained_model_"+schemes[schemes_index]+".pkl", "rb")
        regression_model_list = pickle.load(the_file)

        part_data = []
        part_data_predict = []
        iteration_index = 0
        array_index = 0
        S = array_normalization(all_result_after_each_game_all_result[iteration_index])
        strate_dataset_X = S[:,array_index]

        window_size = 5
        strate_dataset_X_paded = np.insert(strate_dataset_X, 0, np.zeros(window_size))

        strate_dataset_window_X = np.array([[strate_dataset_X_paded[i + j] for i in range(window_size)] for j in
                                             range(strate_dataset_X_paded.shape[0] - window_size)])

        part_data_predict = regression_model_list[array_index].predict(strate_dataset_window_X)
        # print(S_pred)

        for S_array in S:
            part_data.append(S_array[array_index])

        # for S_array in S_pred:
        #     part_data_predict.append(S_array[array_index])
        # print(part_data)
        # print(part_data_predict)

        plt.figure(figsize=(figure_width, figure_high))
        plt.plot(range(len(part_data)), part_data, label="Original Data")
        plt.plot(range(1,len(part_data)+1), part_data, label="No Predict Data")
        plt.plot(range(len(part_data)), part_data_predict, label="Predict Data")
        plt.legend()
        plt.show()




if __name__ == '__main__':
    # schemes = ["DD-IPI", "DD-ML-IPI", "DD-Random-IPI"]
    schemes = ["DD-IPI", "DD-PI"]
    window_size = 5
    n_neighbors = 100
    strategy_number = 8
    generate_trained_ML(schemes,window_size,n_neighbors, strategy_number)
    # display_prediction_result(schemes, strategy_number)
    print('The scikit-learn version is {}.'.format(sklearn.__version__))







