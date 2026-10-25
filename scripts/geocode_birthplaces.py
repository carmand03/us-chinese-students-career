"""Match historical birth towns to the supplied local coordinate lookup."""
import re,unicodedata,json
import pandas as pd

def normalize(value):
    if pd.isna(value):return ''
    value=unicodedata.normalize('NFKD',str(value)).casefold()
    return ''.join(c for c in value if c.isalnum() and not unicodedata.combining(c))

def bilingual(value):
    value='' if pd.isna(value) else str(value).strip()
    m=re.search(r'[\u3400-\u9fff]',value)
    return [v for v in [normalize(value[:m.start()] if m else value),normalize(value[m.start():] if m else '')] if v]

def geocode_birthplaces(main,lookup):
    lookup=lookup.copy()
    for c in ['Latitude','Longitude']:
        lookup[c+'_parsed']=pd.to_numeric(lookup[c].astype(str).str.strip().str.replace(',','.',regex=False),errors='coerce')
    lookup['valid_coordinates']=lookup.Latitude_parsed.between(-90,90)&lookup.Longitude_parsed.between(-180,180)
    index={}
    for i,r in lookup.iterrows():
        for province in bilingual(r.Province):
            for town in bilingual(r.City):index.setdefault((province,town),set()).add(i)
    result=[]
    for r in main.itertuples():
        provinces={normalize(r.Birth_province_py_st),normalize(r.Birth_province_zh_st)}-{''}
        towns={normalize(r.Birth_town_py),normalize(r.Birth_town_zh)}-{''}
        candidates=set().union(*(index.get((p,t),set()) for p in provinces for t in towns)) if provinces and towns else set()
        valid=lookup.loc[sorted(candidates)]
        valid=valid.loc[valid.valid_coordinates]
        coords=valid[['Latitude_parsed','Longitude_parsed']].drop_duplicates()
        status='matched' if len(coords)==1 else 'ambiguous' if len(coords)>1 else 'invalid_lookup_coordinates' if candidates else 'missing_town' if not towns else 'missing_province' if not provinces else 'unmatched'
        matched=status=='matched'
        notes='; '.join(dict.fromkeys(str(x) for x in valid.Notes.dropna())) if matched else ''
        source_ids='|'.join(valid['#'].astype(str)) if matched else ''
        result.append({'NameID':r.NameID,'Birth_province_py_st':r.Birth_province_py_st,'Birth_town_py':r.Birth_town_py,'Birth_town_zh':r.Birth_town_zh,
                       'birth_geocode_status':status,'birth_lat':float(coords.iloc[0].Latitude_parsed) if matched else None,'birth_lon':float(coords.iloc[0].Longitude_parsed) if matched else None,
                       'birth_lookup_ids':source_ids,'birth_lookup_city':' | '.join(dict.fromkeys(valid.City)) if matched else '',
                       'birth_coordinate_precision':('province proxy in lookup' if 'province-level' in notes.lower() else 'locality reference in lookup') if matched else '',
                       'birth_coordinate_notes':notes,'birth_candidate_ids':'|'.join(lookup.loc[sorted(candidates),'#'].astype(str)) if candidates else ''})
    return pd.DataFrame(result),lookup
