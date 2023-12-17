from flask import Flask, jsonify,make_response,request, render_template, send_from_directory
import jwt
import datetime
from functools import wraps
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.manifold import MDS
from matplotlib.figure import Figure
from flask_cors import CORS


# Initialize
app = Flask(__name__, template_folder='client/build')
app.config['SECRET_KEY'] = 'this_is_security_key'
data = pd.read_csv('./data/Cluster_ContentBased.csv')
df = data.set_index('candidate_id')

CORS(app)

def mkdir_p(mypath):
    '''Creates a directory. equivalent to using mkdir -p on the command line'''

    from errno import EEXIST
    from os import makedirs,path
    try:
        makedirs(mypath)
    except OSError as exc:
        if exc.errno == EEXIST and path.isdir(mypath):
            pass
        else: raise
def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        if 'token' in request.headers:
            token = request.headers['token']
        if not token:
            return jsonify({'mesage':'Token is missing'}),403
        try:
            data = jwt.decode(token,app.config['SECRET_KEY'])
        except:
            return jsonify({'message':'Token is invalid!'}),403
        return f(*args,**kwargs)
    return decorated

@app.route('/')
def index_redir():
    # Reached if the user hits example.com/ instead of example.com/index.html
    return render_template('index.html')

@app.route('/login')
def login():
    auth = request.authorization

    if auth and auth.password =='888888':
        token = jwt.encode({'user':auth.username,'exp':datetime.datetime.utcnow()+datetime.timedelta(minutes=10)},app.config['SECRET_KEY'])
        return jsonify({'token':token.decode('UTF-8')})
    return make_response('Could not verify!',401,{'WWW-Authenticate':'Basic realm="Login Required"'})

@app.route('/main',methods=['GET'])
# @token_required
def find_top_n_closest():
    try:
        usr_id = int(request.args.get('user_id'))
        n = int(request.args.get('num'))
        dataframe = df

        # Vectorized user info
        user = dataframe.loc[usr_id].to_numpy()

        # Generate dissimilarites mattrix and candidates_id from cluster
        dissim_matrix = dataframe.loc[dataframe['Cluster'] == user[0]]
        dissim_matrix = dissim_matrix.drop(labels=usr_id, axis=0)

        candidates_id = dissim_matrix.index.tolist()
        dissim_matrix = dissim_matrix.to_numpy()
        # Calculate dissimilarities matrix to ranking

        dissim_matrix = (dissim_matrix != user.reshape(1, user.shape[0])).sum(axis=1)

        # Sorting
        top_dict = {candidates_id[i]: dissim_matrix[i] for i in range(len(candidates_id))}
        sorted_tuples = sorted(top_dict.items(), key=lambda item: item[1])[:n]

        # Scale Data by MinMaxScaler and MultiDimensionalScaling
        indexes = [i[0] for i in sorted_tuples]
        disim = [i[1] for i in sorted_tuples]

        indexes = [usr_id] + indexes
        disim = [0] + disim

        df2 = df.loc[indexes]
        df2 = df2.drop(['Cluster'],axis = 1)
        df2.insert(0,'Disim',disim,True)

        df2_ = df2.drop(['Disim'],axis=1)
        df2_scaled = MinMaxScaler().fit_transform(df2_)
        df2_scaled = pd.DataFrame(data= df2_scaled,columns= df2_.columns.tolist())

        embedding = MDS(n_components=2)
        df2_trans = embedding.fit_transform(df2_scaled)
        df2_scaled_transformed = pd.DataFrame(data= df2_trans,columns= ['X','Y'])
        df2_scaled_transformed.insert(0,'Disim',df2['Disim'].tolist(),True)

        #Visualize
        fig = Figure()
        ax1 = fig.add_subplot(2,2,1)
        ax2 = fig.add_subplot(2,2,2)
        ax3 = fig.add_subplot(2,2,3)

        get_min_max = [i for i in disim if i != 0]
        label = pd.Series(df2['Disim'].tolist())
        label1 = [0,min(get_min_max)]
        label2 = df2_scaled_transformed['Disim'].unique().tolist()
        label3 = [0,max(get_min_max)]

        for i in label1:
            ax1.scatter(df2_scaled_transformed[label == i]['X'] , df2_scaled_transformed[label == i ]['Y'] , label = i,)
        for i in label2:
            ax2.scatter(df2_scaled_transformed[label == i]['X'] , df2_scaled_transformed[label == i ]['Y'] , label = i,)
        for i in label3:
            ax3.scatter(df2_scaled_transformed[label == i]['X'] , df2_scaled_transformed[label == i ]['Y'] , label = i,)
        ax1.legend(frameon=True)
        ax1.set_ylim(-2,3)
        ax1.set_xlim(-2,3)
        ax2.legend(frameon=True)
        ax2.set_ylim(-2,3)
        ax2.set_xlim(-2,3)
        ax3.legend(frameon=True)
        ax3.set_ylim(-2,3)
        ax3.set_xlim(-2,3)
        ax1.set_title('Closest Users')
        ax2.set_title(f'Top {n} user closest to {usr_id}')
        ax3.set_title('Last Top Users')
        #Save figure
        output_dir = f"static/{usr_id}"
        mkdir_p(output_dir)
        fig.savefig(f'{output_dir}/{n}.png')
        #Result
        df3 = df.drop(['Cluster'], axis =1)
        diction = {
            'a_user':dict(df3.loc[usr_id])
        }
        sim = [(len(df3.columns) - i[1])/len(df3.columns) for i in sorted_tuples]
        index = [i[0] for i in sorted_tuples]
        df3 = df3.loc[index]
        df3.insert(0, 'Similarity', sim, True)
        candidates = []
        for i in sorted_tuples:
            a = dict(df3.loc[i[0]])
            b = {'candidate_id': i[0]}
            b.update(a)
            candidates.append(b)
        diction['candidates'] = candidates
        diction['url']= f'{output_dir}/{n}.png'
        return diction
    except Exception:
        diction = {
            'a_user': {},
            'candidates': [],
            'url': None
        }
        return diction

# Start
if __name__=='__main__':
    app.run(host='0.0.0.0', port='5005')