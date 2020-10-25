import numpy as np
import pandas as pd

def get_dist_between(x, cutoff=3):
    sele1 = x[0]
    sele2 = x[1]
    sele1_pos = sele1.positions
    sele2_pos = sele2.positions
    pos = (sele1_pos[:, np.newaxis] - sele2_pos)
    
    reshaped = pos.reshape(-1, sele1_pos.shape[1])
    dist = np.sum(np.abs(reshaped)**2,axis=1)**(1./2)
    dist = dist.reshape(pos.shape[0], pos.shape[1])
    
    ids = np.where(dist<cutoff)
    vals = dist[ids]
    
    conv = lambda sele, ids: [f"{resid}{resname}_{name}"\
                 for resid, resname, name in zip( sele.resid[ids], sele.resname[ids], sele.name[ids] )]
    
    return conv(sele1, ids[0]), conv(sele2, ids[1]), vals
    
def pairwise_fingerprint(x, nres=3, cutoff=10):    
    da1 = get_dist_between(x, cutoff=cutoff)
    df = pd.DataFrame(da1).T
    df.columns = ['Ligand', 'Receptor', 'Dist']
        
    ## find min dist between each lig atom and each receptor
    # get min dist for each lig receptro atom combo
    df = df.groupby(['Ligand', 'Receptor']).min()
    # drop receptor column
    df = df.reset_index().drop('Receptor', axis=1)
        
    ## find nres min values for each lig atom
    # func to sort series and return first nres min values
    # rest of the series values are but as nan, to maintain size
    min_n = lambda y: y.sort_values()[:nres].append(pd.Series([np.nan]*(len(y)-nres)))
        
    # call func for each ligand atom, and drop nan vals
    vals = df.groupby('Ligand').transform(min_n).dropna()['Dist'].to_numpy()
        
    return vals