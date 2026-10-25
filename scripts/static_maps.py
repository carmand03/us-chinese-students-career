"""Optional static choropleth exports. Run after workflow.py."""
from pathlib import Path
import json, os
import pandas as pd
os.environ.setdefault('MPLCONFIGDIR',str(Path.cwd()/'.matplotlib_cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.cm import ScalarMappable

ROOT=Path(__file__).resolve().parent
us=json.loads((ROOT/'assets/us_states.geojson').read_text())
cn=json.loads((ROOT/'assets/china_provinces.geojson').read_text())
names={'11':'Beijing','12':'Tianjin','13':'Hebei','14':'Shanxi','15':'Inner Mongolia','21':'Liaoning','22':'Jilin','23':'Heilongjiang','31':'Shanghai','32':'Jiangsu','33':'Zhejiang','34':'Anhui','35':'Fujian','36':'Jiangxi','37':'Shandong','41':'Henan','42':'Hubei','43':'Hunan','44':'Guangdong','45':'Guangxi','46':'Hainan','50':'Chongqing','51':'Sichuan','52':'Guizhou','53':'Yunnan','54':'Tibet','61':'Shaanxi','62':'Gansu','63':'Qinghai','64':'Ningxia','65':'Xinjiang','71':'Taiwan','81':'Hong Kong','82':'Macao'}
for f in cn['features']: f['properties']['name_en']=names.get(str(f['properties']['id']),'Unknown')
cmap=LinearSegmentedColormap.from_list('career_teal',['#dceff0','#0d5c6e'])
fig,axs=plt.subplots(1,2,figsize=(16,7.6),facecolor='#f5f8f8')
fig.subplots_adjust(top=.80,bottom=.20,left=.04,right=.96,wspace=.09)
fig.text(.04,.94,'WHERE APPOINTMENTS WERE RECORDED',fontsize=10,color='#126b73',weight='bold')
fig.text(.04,.885,'Employment by state and province',fontsize=26,color='#183340',weight='bold')
def paint(ax,features,col,counts,maximum,bounds):
    norm=Normalize(0,maximum)
    for f in features:
        n=counts.get(f['properties'][col],0)
        polys=f['geometry']['coordinates'] if f['geometry']['type']=='MultiPolygon' else [f['geometry']['coordinates']]
        for rings in polys:
            ax.add_patch(Polygon(rings[0],facecolor=cmap(norm(n)) if n else '#fff',edgecolor='#8eacb6',lw=.45))
    ax.set_xlim(bounds[0],bounds[1]);ax.set_ylim(bounds[2],bounds[3]);ax.set_aspect(1.22);ax.axis('off')
for ax,geo,file,col,title,bounds in [(axs[0],us,'us_state_counts','name','United States',(-126,-66,24,51)),(axs[1],cn,'china_province_counts','name_en','Chinese provinces',(73,136,17,54))]:
    t=pd.read_csv(ROOT/'tables'/f'{file}.csv');matched=t[t.matched_boundary]
    by=dict(zip(matched.province,matched.appointments));maximum=int(matched.appointments.max())
    features=[f for f in geo['features'] if f['properties'][col] not in ['Alaska','Hawaii']] if file.startswith('us') else geo['features']
    paint(ax,features,col,by,maximum,bounds)
    ax.set_title(title+'\n'+f'{matched.appointments.sum():,} mapped of {t.appointments.sum():,} appointment records',loc='left',fontsize=15,color='#183340',pad=18)
    bar=fig.colorbar(ScalarMappable(norm=Normalize(0,maximum),cmap=cmap),ax=ax,orientation='horizontal',fraction=.045,pad=.05,shrink=.8)
    bar.set_label('Recorded appointments (independent linear scale)',fontsize=9,color='#415b65');bar.ax.tick_params(labelsize=9);bar.outline.set_visible(False)
    if file.startswith('us'):
        for name,pos,b in [('Alaska',[.045,.24,.16,.19],(-180,-130,50,72)),('Hawaii',[.225,.24,.09,.13],(-161,-154,18,23))]:
            inset=fig.add_axes(pos)
            inset.add_patch(Rectangle((0,0),1,1,transform=inset.transAxes,facecolor='#f5f8f8',edgecolor='#c5d5d9',lw=.8,zorder=-1))
            paint(inset,[f for f in geo['features'] if f['properties']['name']==name],'name',by,maximum,b)
            inset.text(.03,.93,name,fontsize=8,color='#5c7079',transform=inset.transAxes)
fig.text(.04,.105,'Darker teal indicates more recorded appointments. White indicates zero. Missing and unmatched provinces are excluded.',fontsize=10,color='#4e6570')
fig.text(.04,.065,'Modern outlines are reference geography for historical assignments; they do not reconstruct historical boundaries. All appointment statuses included.',fontsize=9,color='#5c7079')
fig.text(.04,.03,'Sources: supplied career.csv; PublicaMundi MappingAPI; longwosion/geojson-map-china. No workplace coordinates required for province counts.',fontsize=8,color='#6d7f87')
fig.savefig(ROOT/'maps/choropleths.png',dpi=180,facecolor=fig.get_facecolor())
fig.savefig(ROOT/'maps/choropleths.svg',facecolor=fig.get_facecolor())
print('Saved static choropleths (PNG and SVG).')
