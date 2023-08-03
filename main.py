from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List
from sqlalchemy.orm import Session 
from sqlalchemy import and_
import crud, models, schemas
import plotly.graph_objects as go
import numpy as np
from database import SessionLocal, engine
from geopy.geocoders import Nominatim
from folium.plugins import HeatMap
from wordcloud import WordCloud, STOPWORDS
import folium
import matplotlib.pyplot as plt
import math
import nltk
import collections
# nltk.download('vader_lexicon')
# nltk.download('punkt')
# nltk.download('wordnet')
# nltk.download('omw-1.4')

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

global tot_rests 
tot_rests = 40679

def get_db():
    db = SessionLocal()
    try:
        yield db
    
    finally:
        db.close()

all_locations = ['BTM', 'Banashankari', 'Banaswadi', 'Bannerghatta Road', 'Basavanagudi', 'Basaveshwara Nagar', 'Bellandur', 'Bommanahalli', 'Brigade Road', 'Brookefield',
 'CV Raman Nagar', 'Central Bangalore', 'Church Street', 'City Market', 'Commercial Street', 'Cunningham Road', 'Domlur', 'East Bangalore',
 'Ejipura', 'Electronic City', 'Frazer Town', 'HBR Layout', 'HSR', 'Hebbal', 'Hennur', 'Hosur Road', 'ITPL Main Road, Whitefield', 'Indiranagar',
 'Infantry Road', 'JP Nagar', 'Jakkur', 'Jalahalli', 'Jayanagar', 'Jeevan Bhima Nagar', 'KR Puram', 'Kaggadasapura', 'Kalyan Nagar',
 'Kammanahalli', 'Kanakapura Road', 'Kengeri', 'Koramangala', 'Koramangala 1st Block', 'Koramangala 2nd Block', 'Koramangala 3rd Block', 'Koramangala 4th Block',
 'Koramangala 5th Block', 'Koramangala 6th Block', 'Koramangala 7th Block', 'Koramangala 8th Block', 'Kumaraswamy Layout', 'Langford Town',
 'Lavelle Road', 'MG Road', 'Magadi Road', 'Majestic', 'Malleshwaram', 'Marathahalli', 'Mysore Road', 'Nagarbhavi', 'Nagawara',
 'New BEL Road', 'North Bangalore', 'Old Airport Road', 'Old Madras Road', 'Peenya', 'RT Nagar', 'Race Course Road', 'Rajajinagar',
 'Rajarajeshwari Nagar', 'Rammurthy Nagar', 'Residency Road', 'Richmond Road', 'Sadashiv Nagar', 'Sahakara Nagar', 'Sanjay Nagar', 'Sankey Road',
 'Sarjapur Road', 'Seshadripuram', 'Shanti Nagar', 'Shivajinagar', 'South Bangalore', 'St. Marks Road', 'Thippasandra', 'Ulsoor', 'Uttarahalli',
 'Varthur Main Road, Whitefield', 'Vasanth Nagar', 'Vijay Nagar', 'West Bangalore', 'Whitefield', 'Wilson Garden', 'Yelahanka', 'Yeshwantpur']

all_locs = ['Bangalore ' + str(i) for i in all_locations]

rest_types = ['Bakery', 'Beverage Shop', 'Cafe', 'Dessert Parlor', 'Food Court', 'Kiosk', 'Quick Bites', 'Sweet Shop', 'Bar', 'Casual Dining',
 'Lounge', 'Pub', 'Bhojanalya', 'Irani Cafee', 'Microbrewery', 'Club', 'Confectionery', 'Delivery', 'Dhaba', 'Fine Dining',
 'Food Truck', 'Mess', 'Pop Up', 'Meat Shop', 'Takeaway']

cuisines = ['Afghan', 'Afghani', 'African', 'American', 'Andhra', 'Arabian', 'Asian', 'Assamese', 'Australian', 'Awadhi', 'BBQ', 'Bakery',
 'Bar Food', 'Belgian', 'Bengali', 'Beverages', 'Bihari', 'Biryani', 'Bohri', 'British', 'Bubble Tea', 'Burger', 'Burmese', 'Cafe',
 'Cantonese', 'Charcoal Chicken', 'Chettinad', 'Chinese', 'Coffee', 'Continental', 'Desserts', 'Drinks Only', 'European', 'Fast Food', 'Finger Food',
 'French', 'German', 'Goan', 'Greek', 'Grill', 'Gujarati', 'Healthy Food', 'Hot dogs', 'Hyderabadi', 'Ice Cream', 'Indian', 'Indonesian',
 'Iranian', 'Italian', 'Japanese', 'Jewish', 'Juices', 'Kashmiri', 'Kebab', 'Kerala', 'Konkan', 'Korean', 'Lebanese', 'Lucknowi', 'Maharashtrian',
 'Malaysian', 'Malwani', 'Mangalorean', 'Mediterranean', 'Mexican', 'Middle Eastern', 'Mithai', 'Modern Indian', 'Momos', 'Mongolian', 'Mughlai',
 'Naga', 'Nepalese', 'North Eastern', 'North Indian', 'Oriya', 'Paan', 'Pan Asian', 'Parsi', 'Pizza', 'Portuguese', 'Rajasthani', 'Raw Meats',
 'Roast Chicken', 'Rolls', 'Russian', 'Salad', 'Sandwich', 'Seafood', 'Sindhi', 'Singaporean', 'South American', 'South Indian',
 'Spanish', 'Sri Lankan', 'Steak', 'Street Food', 'Sushi', 'Tamil', 'Tea', 'Tex-Mex', 'Thai', 'Tibetan', 'Turkish', 'Vegan', 'Vietnamese', 'Wraps']

listed_in_types = ['Buffet', 'Cafes', 'Delivery', 'Desserts', 'Dine-out', 'Drinks & nightlife', 'Pubs and bars']

@app.get("/")
async def hello(request: Request):
    # print(len(cuisines))
    cuisines_ = []
    for i in range(11):
        tmp = cuisines[i*10:(i+1)*10]
        cuisines_.append(tmp)
    # print(len(cuisines_)*len(cuisines_[0]))
    return templates.TemplateResponse("questionnaire.html", {"request": request, "locations": all_locations, "rest_types": rest_types, "cuisines": cuisines, "listed_in": listed_in_types})

@app.get("/plot/{plotname}")
async def givePlot(plotname: str):
    return FileResponse("templates/plots/"+plotname+".html")

@app.post("/process/") 
async def process(request: Request, db: Session = Depends(get_db), name: str = Form(), onl_ord: str = Form(), tbl_bk: str = Form(), locations: str = Form(), rests: str = Form(), dropdown_group: List[str] = Form(), cost: str = Form(), listed_in: str = Form()):
    #getting filtered restaurants based on all submitted parameters 
    onl_ord_int = 1 if onl_ord == 'Yes' else 0
    tbl_bk_int = 1 if tbl_bk == 'Yes' else 0
    _onl_ord = db.query(models.ZomatoData).filter(models.ZomatoData.onl_ord == onl_ord_int).count()
    _tbl_bk = db.query(models.ZomatoData).filter(models.ZomatoData.tbl_bk == tbl_bk_int).count()
    _costs_rate_yes = [i[0] for i in list(db.query(models.ZomatoData.rating).filter(and_(models.ZomatoData.cost >= int(cost)-400, models.ZomatoData.cost <= int(cost)+400, models.ZomatoData.tbl_bk==1)).all())]
    _costs_rate_no = [i[0] for i in list(db.query(models.ZomatoData.rating).filter(and_(models.ZomatoData.cost >= int(cost)-400, models.ZomatoData.cost <= int(cost)+400, models.ZomatoData.tbl_bk==0)).all())]

    #analysing according to each parameter
#######################################################################################################################################

    #ratio of online order
    labels = ['Yes', 'No']
    values = []
    if onl_ord == 'Yes':
        values.append(_onl_ord)
        values.append(tot_rests-_onl_ord)
    else:
        values.append(tot_rests-_onl_ord)
        values.append(_onl_ord)
    
    fig_onl = go.Figure(data=[go.Pie(labels=labels, values=values)])
    fig_onl.update_traces(textfont_color=['#FFFFFF'] ,marker=dict(colors=['#47B39C', '#FFC154'], line=dict(color="#FFFFFF", width=3)))
    fig_onl.update_layout(title="Ratio of Online Order vs No Online Order")
    fig_onl.write_html('templates\plots\onl_ord.html')

    p1_msg = "As seen above, majority of the restaurants prefer to make the option of online ordering available."
    
#######################################################################################################################################

    #scatter plot of cost vs rating of people with/without online order
    cost_range = [i for i in range(int(cost)-400, int(cost)+450, 50)]

    fig_cost_rate = go.Figure()
    fig_cost_rate.add_trace(go.Scatter(
        x=_costs_rate_yes, y=cost_range,
        name="Table Booking",
        mode='markers',
        marker_color="#094164"
    ))

    fig_cost_rate.add_trace(go.Scatter(
        x=_costs_rate_no, y=cost_range,
        name='No Table Booking',
        mode='markers',
        marker_color="#A0270B"
    ))

    fig_cost_rate.update_layout(title="Cost vs Rating", xaxis_title="Ratings", yaxis_title="Approx cost for two people")
    fig_cost_rate.write_html('templates\plots\cost_rating.html')

    tags_pos = db.query(models.Reviews).select_from(models.Reviews).join(models.ZomatoData, and_(models.Reviews.rest_name==models.ZomatoData.rest_name, models.Reviews.tag=='pos', models.ZomatoData.cost >= int(cost)-400, models.ZomatoData.cost <= int(cost)+400)).count()
    tags_neg = db.query(models.Reviews).select_from(models.Reviews).join(models.ZomatoData, and_(models.Reviews.rest_name==models.ZomatoData.rest_name, models.Reviews.tag=='neg', models.ZomatoData.cost >= int(cost)-400, models.ZomatoData.cost <= int(cost)+400)).count()

    p2_msg = ""
    if tags_pos > tags_neg:
        p2_msg += "Our sources tell us that people who offer services in the range of Rs. " +str(int(cost)-400)+ " to Rs. " +str(int(cost)+400)+ " approximately for two people tend to have more positive feedback than negative."
    else:
        p2_msg += "Our sources tell us that people who offer services in the range of Rs. " +str(int(cost)-400)+ " to Rs. " +str(int(cost)+400)+ " approximately for two people tend to have more negative feedback than positive."
#######################################################################################################################################

    #heatmap of number of restaurants in your area 
    geolocator = Nominatim(user_agent="app")
    lat = [12.911275849999999, 12.965283249999999, 13.0141618, 12.9114375, 12.9417261, 12.9933829, 12.93103185, 12.9089453, 12.9736132, 12.9624267,
    12.9854892, 12.97339325, 12.9755105, 12.965717999999999, 12.9822323, 12.9871119, 12.9624669, 12.992303549999999, 12.945245, 12.848759900000001,
    12.996845, 13.0358698, 12.9116225, 13.0382184, 13.0258087, 12.9212213, np.nan, 12.9732913, 12.9837879, 12.9072515, 13.0784743, 13.0464531, 12.9292731,
    12.9678074, 13.007516, 12.9846713, 13.0221416, 13.0093455, 12.8799448, 12.9176571, 12.9340114, 12.9277245, 12.9243692, 12.9282918,
    12.9327778, 12.9348429, 12.9390255, 12.9364846, 12.9408685, 12.9081487, 12.957998, 12.9749487, 12.9755264, 12.975608, 12.9757079, 13.0027353,
    12.9552572, 12.9361461, 12.95961755, 13.0431413, 13.0358947, 13.039718, 12.958206, 13.0262267, 13.0329419, 13.0227204, 12.9842576, 12.9882338,
    12.9274413, np.nan, 13.0535126, 12.965297, np.nan, 13.0621474, 12.9578658, 12.9976332, 12.920441, 12.9931876, 12.9575547, 12.986391, 12.862467899999999,
    12.9728286, 12.973936, 12.9778793, 12.9055682, np.nan, 12.988721250000001, np.nan, 12.9848519, 12.9696365, 12.9489339, 13.1006982, 13.02383]

    lon = [77.60456543431182, 77.59445195, 77.6518539, 77.5999754, 77.5755021, 77.5389467, 77.6782471, 77.6239038, 77.6074716, 77.71918775,
    77.6679809, 77.61123426914668, 77.6026774, 77.5762705372058, 77.6082954, 77.5948766, 77.6381958, 77.70593990523807, 77.6269144, 77.64825295827616,
    77.6130165, 77.6323597, 77.6388622, 77.5919, 77.6305067, 77.6201362, np.nan, 77.6404672, 77.5940558, 77.5782713, 77.6068938, 77.5483803, 77.5824229,
    77.6568367, 77.695935, 77.6790908, 77.6403368, 77.6377094, 77.545857, 77.4837568, 77.6222304, 77.6327822, 77.6242433, 77.6254034, 77.6294052,
    77.6189768, 77.6238477, 77.6134783, 77.617338, 77.5553179, 77.6037312, 77.5997248, 77.6067902, 77.5553564, 77.5728757, 77.5703253, 77.6984163,
    77.5158119, 77.51126721318181, 77.6209093, 77.566958, 77.46441321166122, 77.6676311, 77.7205624, 77.5273253, 77.595715, 77.5877345, 77.554883,
    77.5155224, np.nan, 77.6231566, 77.600367, np.nan, 77.58006135480495, 77.6958748, 77.5844364, 77.6653284, 77.5753419, 77.5979099, 77.6075416,
    77.56089325971044, 77.6013248, 77.6509982, 77.6246697, 77.5455438, np.nan, 77.58516877601824, np.nan, 77.5400626, 77.7497448, 77.5968273, 77.5963454, 77.5529215]

    loc_counts = []
    c = 0
    for i in range(len(all_locations)):
        if math.isnan(lat[i]):
            c += 1
        else:
            tmp = db.query(models.ZomatoData).filter(models.ZomatoData.location==all_locations[i]).count()
            loc_counts.append(tmp)
    
    for i in range(c):
        lat.remove(np.nan)
        lon.remove(np.nan)
    
    data=[[lat[i], lon[i], loc_counts[i]] for i in range(len(loc_counts))]

    baseMap = folium.Map(location=[geolocator.geocode(locations).latitude, geolocator.geocode(locations).longitude], default_zoom_start=12)
    HeatMap(data=data, zoom=20, radius=15).add_to(baseMap)
    baseMap.save("templates\plots\count_heatmap.html")

    p3_msg = "The above plot shows a heatmap of the count of restaurants in the various locations. Weigh the number of your competitors!"
#######################################################################################################################################

    #most popular cuisines
    cuisine_count = {i:0 for i in dropdown_group}
    # print(c_count)
    tmp = db.query(models.ZomatoData.cuisines).all()
    for row in tmp:
        row = row[0].split(', ')
        for item in row:
            if item in dropdown_group:
                cuisine_count[item] += 1

    
    c_count = [i[0] for i in sorted(cuisine_count.items(), key=lambda x: x[1])]
    
    cuisine_count = list(cuisine_count.values())
    # print(cuisine_count)
    x = list(range(max(cuisine_count) + 10))
    fig_cuisines = go.Figure(go.Bar(
        x=cuisine_count, y=dropdown_group, orientation='h'))
    
    fig_cuisines.write_html("templates\plots\cuisine_count.html")

    max_count = c_count[-1]
    least_count = c_count[0]

    p4_msg = "Looks like " +max_count+ " is most in demand. Things are not looking good for " +least_count+ " though!"
    # for cuis in dropdown_group:
    #     if cuis in [i[0].split(' ') for i in db.query(models.ZomatoData.cuisines)]

#######################################################################################################################################

    #count of votes between online order or not
    votes_yes = db.query(models.ZomatoData.votes).filter(models.ZomatoData.onl_ord==1).all()
    votes_no = db.query(models.ZomatoData.votes).filter(models.ZomatoData.onl_ord==0).all()
    votes_yes = [i[0] for i in votes_yes]
    votes_no = [i[0] for i in votes_no]

    trace_yes = go.Box(y=votes_yes, name='Accepting Online Orders', marker = dict(color='rgb(214, 12, 140)'))
    trace_no = go.Box(y=votes_no, name='Not Accepting Online Orders', marker = dict(color='rgb(0, 128, 128)'))

    layout = go.Layout(
        title="Box Plots of count of votes between online order or not"
    )

    data=[trace_yes, trace_no]
    fig = go.Figure(data=data, layout=layout)
    fig.write_html("templates\plots\count_vote.html")

    onl_yes_dict = {'pos': 0, 'neg': 0}
    onl_no_dict = {'pos': 0, 'neg': 0}

    onl_yes_dict['pos'] = db.query(models.Reviews).select_from(models.Reviews).join(models.ZomatoData, and_(models.Reviews.rest_name==models.ZomatoData.rest_name, models.Reviews.tag=='pos', models.ZomatoData.onl_ord==1)).count()
    onl_yes_dict['neg'] = db.query(models.Reviews).select_from(models.Reviews).join(models.ZomatoData, and_(models.Reviews.rest_name==models.ZomatoData.rest_name, models.Reviews.tag=='neg', models.ZomatoData.onl_ord==1)).count()
    onl_no_dict['pos'] = db.query(models.Reviews).select_from(models.Reviews).join(models.ZomatoData, and_(models.Reviews.rest_name==models.ZomatoData.rest_name, models.Reviews.tag=='pos', models.ZomatoData.onl_ord==0)).count()
    onl_no_dict['neg'] = db.query(models.Reviews).select_from(models.Reviews).join(models.ZomatoData, and_(models.Reviews.rest_name==models.ZomatoData.rest_name, models.Reviews.tag=='neg', models.ZomatoData.onl_ord==0)).count()
    # print(onl_yes_dict)
    p5_msg = ""
    if onl_yes_dict['pos'] > onl_yes_dict['neg']:
        fr_more = round(((onl_yes_dict['pos']-onl_yes_dict['neg'])/(onl_yes_dict['pos']))*100, 2)
        p5_msg += "We observed that if online ordering facility is provided to the customers, they tend to give a positive rating approximately " +str(fr_more)+ "% of times than a negative rating! "
    else:
        fr_more = round(((onl_yes_dict['neg']-onl_yes_dict['pos'])/(onl_yes_dict['neg']))*100, 2)
        p5_msg += "We observed that if online ordering facility is provided to the customers, they tend to give a negative rating approximately " +str(fr_more)+ "% of times than a positive rating! "
    
    if onl_no_dict['pos'] > onl_no_dict['neg']:
        fr_more = round(((onl_no_dict['pos']-onl_no_dict['neg'])/(onl_no_dict['pos']))*100, 2)
        p5_msg += "We also observed that if online ordering facility is not provided to the customers, they tend to give a positive rating approximately " +str(fr_more)+ "% of times than a negative rating! "
    else:
        fr_more = round(((onl_no_dict['neg']-onl_no_dict['pos'])/(onl_no_dict['neg']))*100, 2)
        p5_msg += "We also observed that if online ordering facility is not provided to the customers, they tend to give a negative rating approximately " +str(fr_more)+ "% of times than a positive rating! "

    

#######################################################################################################################################

    #wordcloud of cuisines in rest_types
    rest_cuisines = db.query(models.ZomatoData.cuisines).filter(models.ZomatoData.rest_type==rests).all()
    rest_cuisines = [i[0] for i in rest_cuisines]
    rest_cuisines_ = rest_cuisines
    rest_cuisines = ','.join(i for i in rest_cuisines)
    all_words = rest_cuisines.split(',')
    
    wordcloud = WordCloud(max_font_size=None, background_color='white', collocations=False, width=1500, height=1500).generate(rest_cuisines).to_file('static\images\cuisine_wordcloud.png')
    
    rest_cuis_dict = {i:all_words.count(i) for i in all_words}
    top_words = [i[0].strip() for i in sorted(rest_cuis_dict.items(), reverse=True, key=lambda x: x[1])]

    top_words = list(set(top_words[:5]))
    p6_msg = "The above image shows the big names in cuisine offered by the same restaurant type as you. Looks like the buzzwords are "
    for i in range(len(top_words) -1):
        p6_msg += top_words[i] +", "
    
    p6_msg += top_words[-1]+ "."

#######################################################################################################################################


    

    return templates.TemplateResponse("report.html", {"request": request, "rest_name": name, "p1_msg": p1_msg, "p2_msg": p2_msg, "p3_msg": p3_msg, "p4_msg": p4_msg, "p5_msg": p5_msg, "p6_msg": p6_msg})