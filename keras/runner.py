# encoding: utf-8

import sys
import codecs
from lstm_segment import pretraining, training, run_test


# training file 由空格和换行符号分割分词，如：
# "中共中央  总书记  、  国家  主席  江  泽民 \r\n"，看到 '、' 也被空格分开，而换行符用于分割下一行
# 这里比较麻烦的是换行符，遇到换行符，需要把换行符单提出来
# 上例得到 [中共中央, 总书记, 、, 国家, 主席, 江, 泽民, \r\n]
# 注意，不能把全部行都组合到一起，然后按空格和换行符分割，这样会丢掉换行符，只能逐行处理 
def load_train_file(filename):
    segments = []
    train_tags = '' 
    with codecs.open(filename, 'r', 'utf-8') as f:
	# 逐行处理
	for line in f:
	    # 如果使用 split()，\r\n 会被 split 处理掉，而这里希望保留；但 split(' ') 会把中间的 u'' 分出来，需要注意)
	    words = line.split(' ')
            # 逐词处理 tags
            for word in words:
		if len(word) == 1:
		    train_tags += 'S'
		# 这里不能用 else，否则 split 出来的 u'' 会导致错误
		elif len(word) > 1:
		    train_tags += 'B' + 'M' * (len(word) - 2) + 'E'
            # 分词加入 segments
	    segments += words
    # 返回 train_text, train_tags
    return ''.join(segments), train_tags


# 这个就简单多了，本来就没有空格，故此把全部行连在一起返回即可; 其中是包含换行符 \r\n 的
def load_test_file(filename):
    with codecs.open(filename, 'r', 'utf-8') as f:
	return ''.join(f.readlines())


# 把预测的结果写回 out_dir 中的文件
def dump_file(out_dir, test_text, predict_tags, iteration, diversity):
    filename = '{}/output_{}_{}.utf8'.format(out_dir, iteration, diversity)
    with codecs.open(filename, 'w', 'utf-8') as f:
	for tag in predict_tags:
        f.write(u" ".join(segments))


def workflow(train_file, test_file, out_dir, maxlen=7, step=3):
    train_text, train_tags = load_train_file(train_file)
    test_text = load_test_file(test_file)
    X, y, chars, tags, char_indices = pretraining(train_text, train_tags, maxlen, step)
    for i, model in enumerate(training(X, y, maxlen, len(chars), len(tags))):
	for diversity in [0.5, 1, 1.5]:
	    predict_tags = run_test(model, test_text, diversity, maxlen, len(chars), char_indices, tags)
	    assert len(predict_tags) == len(test_text)
	    dumpfile(out_dir, test_text, predict_tags, i, diversity)
	

if __name__ == '__main__':
    pass
