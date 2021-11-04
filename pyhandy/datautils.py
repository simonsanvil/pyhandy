from typing import Union, Callable
import numpy as np
import pandas as pd

def get_data_summary(
    data:pd.DataFrame,
    target:Union[str,Callable]=None,
    target_metric:Union[Callable,dict]=None,
    include_index=True,
    drop_null_stats=True,
    **extra_summary_metrics):
    ''''
    Parameters
    --------
    data:pandas.DataFrame
        Dataframe with the data you wish to summarize
    target:numpy.array/pandas.Series/str (optional)
        The name of a column of the dataframe or numeric numpy array to compare other columns of the dataframe to it and compute correlation with.
    target_metric:Callable or dict (optional)
        Function or dictionary of functions to compare the columns of this dataframe with the target_data. Must 
        accept two arguments corresponding to two vectors to compare. E.g: {'r2_score':sklearn.metrics.r2_score}
    include_index:bool (default=True)
        Whether to include the index of this dataframe in the data summary or not
    drop_null_stats:bool (default=True)
        Whether to drop statistics that are null for all columns in order to remove potentially irrelevant informations from the summary. Default is True (to drop them).
    **extra_summary_metrics
        Dictionary or extra arguments that define the functions/callables of other metrics to compute
        from the columns of the dataframe. The functions defined must only accept one argument corresponding to a column of data
        Warning: remember to take datatypes into account e.g: {'sum_div_2': lambda x: sum(x)/2 if pandas.api.types.is_numeric_dtype(x) else np.nan}
    
    Usage
    ------------
    get_data_summary(df,target_data=y,target_metric=sklearn.metrics.r2_score,StandardDeviation=scipy.stats) #assumes all columns are numeric
    '''
    data = data.copy()
    target_data = data[target] if isinstance(target,str) else target

    if target_data is not None:
        if str(target_data.dtype) in ['category','object'] or 'datetime' in str(target_data.dtype):
            raise TypeError(f'Error: "target" cant\'t be of type {str(target_data.dtype)}')

    if target_metric is None:
        target_metric_dict = {}
    elif isinstance(target_metric,dict):
        target_metric_dict = {name: (lambda x,data_type : f(target_data,x) if data_type not in ['category','object'] and 'datetime' not in data_type and target_data is not None else np.nan) for name,f in target_metric.items()}
    else:
        target_metric_dict = {'MetricWithTarget':lambda x,data_type : target_metric(target_data,x) if data_type not in ['category','object'] and 'datetime' not in data_type and target_data is not None else np.nan}
    
    if target_data is not None:
        if data.isnull().values.any() or any(np.isnan(target_data)) :
            logging.warning("Correlation with target will be computed but there are NaNs in the data given.")

    get_col_summary = lambda col,data_type: {
        'ColumnName': col.name, 
        'DataType': data_type, 
#         'NumMissing': col.isnull().sum(),
        'MissingPercent' : col.isnull().sum()/len(col),
        'CorrelationWithTarget': np.corrcoef(col[~np.isnan(col)],target_data[~np.isnan(target_data)])[0,1] if (data_type not in ['category','object'] and 'datetime' not in data_type and target_data is not None) else np.nan,
        **{name:f(col,data_type) for name,f in target_metric_dict.items()},**{name:f(col,data_type) for name,f in target_metric_dict.items()},
        'Mean': col.mean() if data_type not in ['category','binary','object','datetime64[ns]'] else np.nan, 
        'Median': col.median() if data_type not in ['category','object','datetime64[ns]']  else np.nan,
        'Mode': col.mode().values[0] if 'datetime' not in data_type else np.nan,
        'MinValue': col.min() if data_type not in ['category','binary','object'] else np.nan, 
        'MaxValue': col.max() if data_type not in ['category','binary','object'] else np.nan,
        'NumOfUnique': col.nunique(),
        'UniqueValues': sorted(col.dropna().unique()) if data_type in ['category','binary','object'] else np.nan,
        'FracUnique': list((col.value_counts()/len(col)).round(3)) if data_type in ['category','binary','object'] else np.nan,
        **{name:f(col) for name,f in extra_summary_metrics.items()},
    }
    
    if not str(data.index.dtype).startswith("int") and include_index:
        index_name = data.index.name
        data = data.reset_index().rename(columns={index_name:f"{index_name}*"})
        has_index = True
    else:
        has_index = False
        
    summary_rows = [get_col_summary(data[col],'binary' if data[col].isin([0, 1, np.nan]).all() else str(data[col].dtype)) for col in data.columns]
    info_df = pd.DataFrame(summary_rows, columns=summary_rows[0].keys()).set_index('ColumnName')
    info_df['is_index'] = [ind==data.index.name and has_index for ind in info_df.index]
    info_df = info_df.sort_values(['is_index','DataType','CorrelationWithTarget','ColumnName'], ascending=[False,True,False,True], na_position='last').drop('is_index',axis=1)
    if target_data is None:
        info_df = info_df.drop("CorrelationWithTarget",axis=1)
    print("Dataset has {nrows} rows and {ncols} columns".format(nrows=len(data),ncols=len(data.columns)-has_index))
    if has_index:
        print("(*): dataset's index")
    if drop_null_stats:
        return info_df.dropna(how="all",axis=1)
    else:
        return info_df
