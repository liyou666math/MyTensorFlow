# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import tensorflow as tf

# 定义神经网络结构相关的参数
INPUT_NODE = 784
OUTPUT_NODE = 10

IMAGE_SIZE = 28
NUM_CHANNELS = 1
NUM_LABELS = 10

# 第一层卷积层的尺寸和深度
CONV1_DEEP = 32
CONV1_SIZE = 5
# 第二层卷积层的尺寸和深度
CONV2_DEEP = 64
CONV2_SIZE = 5
# 全连接层的节点个数
FC_SIZE = 512

# 定义卷积神经网络的前向传播过程。
# 这里添加参数 train，用于区分训练和测试过程
# 这个程序将用到 dropout方法
def inference(input_tensor, train, regularizer):
    with tf.variable_scope('layer1-conv1'):
        conv1_weights = tf.get_variable(
                "weight", [CONV1_SIZE, CONV1_SIZE, NUM_CHANNELS, CONV1_DEEP],
                initializer=tf.truncated_normal_initializer(stddev=0.1))
        conv1_biases = tf.get_variable(
                'bias', [CONV1_DEEP], initializer=tf.constant_initializer(0.0))
        
        # 使用边长为5，深度为32的过滤器，移动的步长为1，且全使用0填充
        conv1 = tf.nn.conv2d(
                input_tensor, conv1_weights, strides=[1,1,1,1], padding='SAME')
        relu1 = tf.nn.relu(tf.nn.bias_add(conv1, conv1_biases))
    
    # 实现第二层池化层的前向传播过程。
    # 选用最大池化层，过滤器的边长为2，全零填充，步长为2.
    # 输出为14x14x32的矩阵
    with tf.name_scope('layer2-pool1'):
        pool1 = tf.nn.max_pool(
                relu1, ksize=[1,2,2,1], strides=[1,2,2,1], padding='SAME')
        
    # 声明第三层卷积层的变量并实现前向传播过程
    # 输入为14x14x32的矩阵
    # 输出为14x14x64的矩阵
    with tf.variable_scope('layer3-conv2'):
        conv2_weights = tf.get_variable(
                'weight', [CONV2_SIZE, CONV2_SIZE, CONV1_DEEP, CONV2_DEEP],
                initializer=tf.truncated_normal_initializer(stddev=0.1))
        conv2_biases = tf.get_variable(
                'bias', [CONV2_DEEP],
                initializer=tf.constant_initializer(0.0))
        
        # 使用边长为5，深度为64的过滤器，移动的步长为1，使用全0填充
        conv2 = tf.nn.conv2d(
                pool1, conv2_weights, strides=[1,1,1,1], padding='SAME')
        relu2 = tf.nn.relu(tf.nn.bias_add(conv2, conv2_biases))
    
    # 实现第四层池化层的前向传播过程
    # 输入为14x14x64
    # 输出为7x7x64
    with tf.name_scope('layer4-pool2'):
        pool2 = tf.nn.max_pool(
                relu2, ksize=[1,2,2,1], strides=[1,2,2,1], padding='SAME')
        
    # 将第四层池化层的输出为第五层全连接层的输入格式。
    # 第四层的输入为 7x7x64的矩阵，这里离需要将矩阵拉成一个向量
    pool_shape = pool2.get_shape().as_list()
    # 计算将矩阵拉直成向量之后的长度。pool_shape[0]为一个batch中数据的个数
    nodes = pool_shape[1] * pool_shape[2] * pool_shape[3]
    
    # 通过 tf.reshape函数将四底层的输出变成一个batch的向量
    reshaped = tf.reshape(pool2, [pool_shape[0], nodes])
    
    # 声明第五层全连接层的变量病实现前向传播过程
    with tf.variable_scope('layer5-fc1'):
        fc1_weights = tf.get_variable(
                'weight', [nodes, FC_SIZE],
                initializer=tf.truncated_normal_initializer(stddev=0.1))
        # 只有全连接层的权重需要加入正则化
        if regularizer != None:
            tf.add_to_collection('losses', regularizer(fc1_weights))
        fc1_biases = tf.get_variable(
                'bias', [FC_SIZE], initializer=tf.constant_initializer(0.1))
        
        fc1 = tf.nn.relu(tf.matmul(reshaped, fc1_weights) + fc1_biases)
        if train: fc1 = tf.nn.dropout(fc1, 0.5)
        
    # 声明第六层全连接层的变量并实现前向传播过程
    # 输入为长度为512的向量
    # 输出为一组长度为10的向量
    with tf.variable_scope('layer6-fc2'):
        fc2_weights = tf.get_variable(
                'weight', [FC_SIZE, NUM_LABELS],
                initializer=tf.truncated_normal_initializer(stddev=0.1))
        if regularizer != None:
            tf.add_to_collection('losses', regularizer(fc2_weights))
        fc2_biases = tf.get_variable(
                'bias', [NUM_LABELS],
                initializer=tf.constant_initializer(0.1))
        logit = tf.matmul(fc1, fc2_weights) + fc2_biases
        
    # 返回第六层的输出
    return logit