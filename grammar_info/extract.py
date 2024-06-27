import pandas as pd


if __name__ == '__main__':
    # extract predicts
    df = pd.read_csv('./predicts_table.txt', sep='\t')
    names = df.columns
    with open('./predicts_list.txt', 'w') as f:
        for i in range(len(df)):
            line = f'{i+1}\t' + '\t'.join(names[df.iloc[i,:] == '+']) + '\n'
            f.writelines(line)


    # extract follows
    df = pd.read_csv('./follows_table.txt', sep='\t')
    names = df.columns
    with open('./follows_list.txt', 'w') as f:
        for i in range(len(df)):
            line = f'{df.index[i]}\t' + '\t'.join(names[df.iloc[i,:] == '+']) + '\n'
            f.writelines(line)
