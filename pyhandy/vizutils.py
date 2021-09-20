import matplotlib.pyplot as plt
import numpy as np

def subplotted(iterable,ncols=2,figsize=None,zipped=True ,**kwargs):
    if isinstance(iterable,int):
        iterable = range(iterable)
    total_rows = np.ceil(len(iterable)/ncols).astype(int)
    figsize = figsize if figsize is not None else (ncols*10,total_rows*6)
    fig, axes = plt.subplots(total_rows,ncols,figsize=figsize,**kwargs)
    axes = np.atleast_2d(axes)
    axlist = [ax for subl in axes for ax in subl]#[0:len(iterable)]
    if len(axlist) > len(iterable):
        for ax in axlist[len(iterable):]:
            ax.axis('off')
    if zipped:
        return zip([fig for _ in axlist],axlist,iterable)
    else:
        return (fig,axlist,iterable)

def _search_styles(style):
    found = False
    json_path_1 = os.path.join(os.getcwd(),'themes.json')
    json_path_2 = os.path.join(os.path.dirname(os.path.abspath(__file__)),'themes.json')
    if os.path.isfile(style):
        return style
    if os.path.isfile(json_path_1) :
        json_styles = json.load(open(json_path_1,'r'))
        if style in json_styles['themes']:
            return json_styles['themes'][style]
    if os.path.isfile(json_path_2):
        json_styles = json.load(open(json_path_2,'r'))
        if style in json_styles['themes']:
            return json_styles['themes'][style]
    if style in plt.style.available:
        found = style
    
    return found

def get_available_styles():
    styles = plt.style.available
    json_path_1 = os.path.join(os.getcwd(),'themes.json')
    json_path_2 = os.path.join(os.path.dirname(os.path.abspath(__file__)),'themes.json')
    if os.path.isfile(json_path_1):
        json_styles = json.load(open(json_path_1,'r'))
        if 'themes' in json_styles:
            styles = list(json_styles['themes']) + styles
    if os.path.isfile(json_path_2):
        json_styles = json.load(open(json_path_2,'r'))
        if 'themes' in json_styles:
            styles = list(json_styles['themes']) + styles
    return styles

def plot_dfs_comparison(df1,df2,label1=None,label2=None, remove_outliers=False,outlier_thresh=3,title_add='',figsize=None,**kwargs):            
    df1, df2 = df1.copy(), df2.copy()
    if remove_outliers:
        df1 = df1.apply(lambda x: np.where(np.abs(x-x.mean())/x.std()>outlier_thresh,np.nan,x) ,axis=0)
        df2 = df2.apply(lambda x: np.where(np.abs(x-x.mean())/x.std()>outlier_thresh,np.nan,x) ,axis=0)
            
    for fig,ax,col in subplotted(df1.columns,figsize=figsize,**kwargs):        
        ax.plot(df1.index,df1[col],label=label1)
        ax.plot(df2.index,df2[col],label=label2)
        ax.set_title("Plot of " + col+title_add);
        ax.legend();
    
    return fig