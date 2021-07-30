from flask import render_template, request, Blueprint, flash, redirect, url_for,session
from flaskblog.models import Post, Comment, Brandname, Catagoryname, SellerId, User, Product ,CustomerOrder, Blog
from flaskblog.main.forms import Contact, Brand, Catagory, Sellerform,Addproducts,Upproducts
from flaskblog import db, bcrypt
from flask import request,make_response
import requests
from flaskblog.users.utils import get_country ,call_api
from flask_login import current_user, login_required
from flaskblog.users.utils import save_pro_picture ,send_email
import secrets
import json
import pdfkit
import stripe

config=pdfkit.configuration(wkhtmltopdf=r'.\flaskblog\bin\wkhtmltopdf.exe')
buplishable_key ='pk_test_51IJhisCvsB7CERUXznrhAbCUHPmY1WDcqwnseIFRVLWiQHs49EgchoODlorCmpCkYnKOx4CtyPOJeNTEx7ksU8bS00Am5A3LR4'
stripe.api_key ='sk_test_51IJhisCvsB7CERUX2Gq7tiMiSMT2VecnDuc5mlfPp3bbGaWHGpfmbTgJ6OimECeEQ1C8Tw2HD84q5iNS1JZKSkMr00iXJwgdXx'

main = Blueprint('main', __name__)

def MagerDicts(dict1,dict2):
	if isinstance(dict1, list) and isinstance(dict2,list):
		return dict1  + dict2
	if isinstance(dict1, dict) and isinstance(dict2, dict):
		return dict(list(dict1.items()) + list(dict2.items()))

@main.route("/")
def index():

	return render_template('index.html')

@main.route("/community/post")
def home():
	page = request.args.get('page', 1, type=int)
	posts = Post.query.filter_by(status='approve').order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
	return render_template('home.html', posts=posts ,title='Community')

@main.route("/community/blog")
def home_blog():
	page = request.args.get('page', 1, type=int)
	posts = Blog.query.filter_by(status='approve').order_by(Blog.date_posted.desc()).paginate(page=page, per_page=5)
	return render_template('home_blog.html', posts=posts ,title='Community_blog')


@main.route("/about")
def about():
	form = Contact()
	if form.validate_on_submit():
		flash('Your post has been created!', 'success')
		return redirect(url_for('main.index'))

	return render_template('about.html', title='About' , form=form)



@main.route("/addwriters", methods=['GET', 'POST'])
@login_required
def brands():
	if current_user.username == 'lampofcheer' or current_user.type == 'admin':
		a = 1
	elif current_user.status != 'approve':
		return "<h2>Please wait for account approve. it may take upto 12 hours.</h2>"
	if current_user.is_authenticated:
		if current_user.type == "admin" or current_user.username == 'lampofcheer':
			form = Brand()
			if form.validate_on_submit():
				bran = Brandname(brand_name=form.name.data, brand_det=form.shortdis.data)
				db.session.add(bran)
				db.session.commit()
				res = User.query.filter_by(type='admin')
				body = 'writer name: '+form.name.data + ' discription : '+form.shortdis.data + " by " + current_user.email + ' , ' + current_user.username
				send_email(res,'New Writer added',body)
				flash('Your post has been created!', 'success')
				return redirect(url_for('main.index'))
			return render_template('brand.html', title='Add Brand' , form=form)
	return "<h3>Admin Login Required.</h3>"

@main.route("/addcatagories", methods=['GET', 'POST'])
@login_required
def catagories():
	if current_user.username == 'lampofcheer' or current_user.type == 'admin':
		a = 1
	elif current_user.status != 'approve':
		return "<h2>Please wait for account approve. it may take upto 12 hours.</h2>"
	if current_user.is_authenticated:
		if current_user.type == "admin" or current_user.username == 'lampofcheer':
			form = Catagory()
			if form.validate_on_submit():
				cata = Catagoryname(catagory_name=form.name.data, catagory_det=form.shortdis.data)
				db.session.add(cata)
				db.session.commit()
				res = User.query.filter_by(type='admin')
				body = 'Catagory name: '+form.name.data + ' discription : '+form.shortdis.data + " by " + current_user.email + ' , ' + current_user.username
				send_email(res,'New Catagory added',body)
				flash('Your post has been created!', 'success')
				return redirect(url_for('main.index'))
			return render_template('catagory.html', title='Add Catagory' , form=form)
	return "<h3>Admin Login Required.</h3>"

@main.route("/panel/registration", methods=['GET', 'POST'])
def sellerreg():
	if current_user.is_authenticated:
		return redirect(url_for('main.index'))
	else:
		form = Sellerform()
		if form.validate_on_submit():
			hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
			user = User(username=form.username.data, email=form.email.data, password=hashed_password,birth_date=form.birth_date.data,type='panel')
			sellid=SellerId(username=form.username.data, email=form.email.data, birth_date=form.birth_date.data,password=form.password.data,trade=form.Parents_No.data,nid=form.nid.data,phone=form.phone.data,address=form.address.data,shopname=form.panel.data)
			db.session.add(sellid)
			db.session.add(user)
			db.session.commit()
			res = User.query.filter_by(type='admin')
			body = 'panel name: '+form.Username.data +form.username.data+ " email " +form.email.data+ ' birth date '+ form.birth_date.data + ' hashed_password ' + str(hashed_password) + 'additional no '+ form.Parents_No.data + ' NID ' +form.nid.data+ ' Phone No ' +form.phone.data+ ' address ' +form.address.data+ ' panel ' + form.panel.data
			send_email(res,'New Panel added',body)
			return redirect(url_for('main.index'))
	return render_template('seller.html', title='Panel registration',form=form)

@main.route('/panel/addbook', methods=['GET','POST'])
@login_required
def adddproduct():
	if current_user.username == 'lampofcheer' or current_user.type == 'admin' or current_user.type == 'panel':
		a = 1
	elif current_user.status != 'approve':
		return "<h2>Please wait for account approve. it may take upto 12 hours.</h2>"
	if current_user.is_authenticated:
		if current_user.username == 'lampofcheer' or current_user.type == 'admin' or current_user.type == 'panel':
			brands = Brandname.query.all()
			categories = Catagoryname.query.all()
			form = Addproducts()
			if form.validate_on_submit():
				name = form.name.data
				price = form.page.data
				discount = form.link.data
				stock = form.stock.data
				#colors = form.colors.data
				desc = form.discription.data
				brand = request.form.get('brand')
				category = request.form.get('category')
				image_1 = save_pro_picture(form.image_1.data)
				image_2 = save_pro_picture(form.image_2.data)
				image_3 = save_pro_picture(form.image_3.data)
				product = Product(name=name,page=price,link=discount,stock=stock,desc=desc,category=category,brand=brand,image_1=image_1,image_2=image_2,image_3=image_3,author5=current_user)
				db.session.add(product)
				#print(product)
				flash('Your product has been added!', 'success')
				#flash(f'The product {name} was added in database','success')
				db.session.commit()
				res = User.query.filter_by(type='admin')
				body = 'writer name: '+request.form.get('brand') + ' category : '+request.form.get('category') +' name '+form.name.data+ " by " + current_user.email + ' , ' + current_user.username
				send_email(res,'New Book added',body)
				return redirect(url_for('main.index'))
			else:
				print(form.errors.items())
	else:
		return "<h3>Seller Shop Login Required.</h3>"
	return render_template('product.html', form=form, title='Add a Product', brands=brands,categories=categories)


@main.route('/panel/book', methods=['GET','POST'])
@login_required
def seller_product():
	if current_user.username == 'lampofcheer' or current_user.type == 'admin'  or current_user.type == 'panel':
		a = 1
	elif current_user.status != 'approve':
		return "<h2>Please wait for account approve. it may take upto 12 hours.</h2>"
	brands = Brandname.query.all()
	categories = Catagoryname.query.all()
	if current_user.is_authenticated:
		if current_user.type == 'panel':
			product = Product.query.filter_by(author5=current_user)
		elif current_user.type == 'admin' or current_user.username == 'lampofcheer':
			product = Product.query.all()				
			brands = Brandname.query.all()
			categories = Catagoryname.query.all()
		else:
			return "<h3>Admin or panel Login Required.</h3>"

	else:
		return "<h3>Admin or panel Login Required.</h3>"

	return render_template('selleradmin.html', title='Products', brands=brands,categories=categories,products=product)

@main.route('/panel/book/<int:id>/update', methods=['GET','POST'])
@login_required
def product_update(id):
	if current_user.username == 'lampofcheer' or current_user.type == 'admin' or current_user.type == 'panel':
		a = 1
	elif current_user.status != 'approve':
		return "<h2>Please wait for account approve. it may take upto 12 hours.</h2>"
	if current_user.is_authenticated:
		if current_user.type == 'panel' or current_user.type=='admin' or current_user.username == 'lampofcheer':
			brands = Brandname.query.all()
			categories = Catagoryname.query.all()
			pro=Product.query.filter_by(id=id).first()
			form = Upproducts()
			if form.validate_on_submit():
				pro.name = form.name.data
				pro.page = form.page.data
				pro.link = form.link.data
				pro.stock = form.stock.data
				#pro.colors = form.colors.data
				pro.desc = form.discription.data
				pro.brand = request.form.get('brand')
				pro.category = request.form.get('category')
				if form.image_1.data:
					pro.image_1 = save_pro_picture(form.image_1.data)
				if form.image_2.data:
					pro.image_2 = save_pro_picture(form.image_2.data)
				if form.image_3.data:
					pro.image_3 = save_pro_picture(form.image_3.data)
				db.session.commit()
				res = User.query.filter_by(type='admin')
				body = 'writer name: '+request.form.get('brand') + ' category : '+request.form.get('category') +' name '+form.name.data+ " by " + current_user.email + ' , ' + current_user.username
				send_email(res,'Book Updated',body)
				return redirect(url_for('main.index'))
			elif request.method == 'GET':
				form.name.data = pro.name
				form.page.data = pro.page
				form.link.data = pro.link
				form.stock.data = pro.stock
				#form.colors.data = pro.colors
				form.discription.data = pro.desc
			else:
				print(form.errors.items())


	else:
		return "<h3>Admin or panel Login Required.</h3>"

	return render_template('update_product.html', form=form, title='Product Update', brands=brands,categories=categories)


@main.route('/panel/book/<int:id>/delete', methods=['GET','POST'])
@login_required
def product_delete(id):
	if current_user.username == 'lampofcheer' or current_user.type == 'admin' or current_user.type == 'panel':
		a = 1
	elif current_user.status != 'approve':
		return "<h2>Please wait for account approve. it may take upto 12 hours.</h2>"
	if current_user.is_authenticated:
		if current_user.type == 'panel' or current_user.type=='admin' or current_user.username == 'lampofcheer':
			brands = Brandname.query.all()
			categories = Catagoryname.query.all()
			pro=Product.query.filter_by(id=id).first()
			db.session.delete(pro)
			db.session.commit()
			res = User.query.filter_by(type='admin')
			body = 'writer name: '+pro.brand + ' category : '+pro.category +' name '+pro.name+ " by " + current_user.email + ' , ' + current_user.username
			send_email(res,'Book Deleted',body)
			flash('Your product has been deleted!', 'success')
			return redirect(url_for('main.seller_product'))

	else:
			return "<h3>Admin or Panel Login Required.</h3>"

@main.route('/dashboard/post/<int:id>/delete', methods=['GET','POST'])
@login_required
def admin_post_delete(id):
	if current_user.username == 'lampofcheer' or current_user.type == 'admin':
		a = 1
	elif current_user.status != 'approve':
		return "<h2>Please wait for account approve. it may take upto 12 hours.</h2>"
	if current_user.is_authenticated:
		if current_user.type == 'admin' or current_user.username == 'lampofcheer':
			brands = Brandname.query.all()
			categories = Catagoryname.query.all()
			post=Post.query.filter_by(id=id).first()
			post.status = 'delete'
			db.session.commit()
			res = User.query.filter_by(type='admin')
			body = post.author.username +','+post.title+" by " + current_user.email + ' , ' + current_user.username
			send_email(res,'post deleted',body)
			flash('Your post has been deleted!', 'success')
			return redirect(url_for('main.dashboard_post_pending'))

	else:
			return "<h3>Admin Login Required.</h3>"



@main.route('/dashboard/account/<int:id>/delete', methods=['GET','POST'])
@login_required
def admin_account_delete(id):
	if current_user.username == 'lampofcheer' or current_user.type == 'admin':
		a = 1
	elif current_user.status != 'approve':
		return "<h2>Please wait for account approve. it may take upto 12 hours.</h2>"
	if current_user.is_authenticated:
		if current_user.type == 'admin' or current_user.username == 'lampofcheer':
			brands = Brandname.query.all()
			categories = Catagoryname.query.all()
			post=User.query.filter_by(id=id).first()
			post.status = 'delete'
			db.session.commit()
			res = User.query.filter_by(type='admin')
			body = post.username +','+post.email+" by " + current_user.email + ' , ' + current_user.username
			send_email(res,'account deleted',body)
			flash('Your post has been deleted!', 'success')
			return redirect(url_for('main.dashboard_account_pending'))

	else:
			return "<h3>Admin Login Required.</h3>"




@main.route('/dashboard/post/<int:id>/approve', methods=['GET','POST'])
@login_required
def admin_post_approve(id):
	if current_user.username == 'lampofcheer' or current_user.type == 'admin':
		a = 1
	elif current_user.status != 'approve':
		return "<h2>Please wait for account approve. it may take upto 12 hours.</h2>"
	if current_user.is_authenticated:
		if current_user.type == 'admin' or current_user.username == 'lampofcheer':
			brands = Brandname.query.all()
			categories = Catagoryname.query.all()
			post=Post.query.filter_by(id=id).first()
			post.status = 'approve'
			db.session.commit()
			res = User.query.filter_by(type='admin')
			body = post.author.username +','+post.title+" by " + current_user.email + ' , ' + current_user.username
			send_email(res,'post approved',body)
			flash('Your post has been approved!', 'success')
			return redirect(url_for('main.dashboard_post_pending'))

	else:
			return "<h3>Admin Login Required.</h3>"




@main.route('/dashboard/account/<int:id>/approve', methods=['GET','POST'])
@login_required
def admin_account_approve(id):
	if current_user.username == 'lampofcheer' or current_user.type == 'admin':
		a = 1
	elif current_user.status != 'approve':
		return "<h2>Please wait for account approve. it may take upto 12 hours.</h2>"
	if current_user.is_authenticated:
		if current_user.type == 'admin' or current_user.username == 'lampofcheer':
			brands = Brandname.query.all()
			categories = Catagoryname.query.all()
			post=User.query.filter_by(id=id).first()
			post.status = 'approve'
			db.session.commit()
			res = User.query.filter_by(type='admin')
			body = post.username +','+post.email+" by " + current_user.email + ' , ' + current_user.username
			send_email(res,'account approved',body)
			flash('Your post has been approved!', 'success')
			return redirect(url_for('main.dashboard_account_pending'))

	else:
			return "<h3>Admin Login Required.</h3>"


@main.route('/dashboard/account/<int:id>/pending', methods=['GET','POST'])
@login_required
def admin_account_pending(id):
	if current_user.username == 'lampofcheer' or current_user.type == 'admin':
		a = 1
	elif current_user.status != 'approve':
		return "<h2>Please wait for account approve. it may take upto 12 hours.</h2>"
	if current_user.is_authenticated:
		if current_user.type == 'admin' or current_user.username == 'lampofcheer':
			brands = Brandname.query.all()
			categories = Catagoryname.query.all()
			post=User.query.filter_by(id=id).first()
			post.status = 'pending'
			db.session.commit()
			res = User.query.filter_by(type='admin')
			body = postusername +','+post.email+" by " + current_user.email + ' , ' + current_user.username
			send_email(res,'account freezed',body)
			flash('Your post has been approved!', 'success')
			return redirect(url_for('main.dashboard_account_approve'))

	else:
			return "<h3>Admin Login Required.</h3>"



@main.route('/library', methods=['GET','POST'])
def show_product():
	brands = Brandname.query.all()
	categories = Catagoryname.query.all()
	page = request.args.get('page', 1, type=int)
	products = Product.query.order_by(Product.name.desc()).paginate(page=page, per_page=5)
	#posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)

	return render_template('show_product.html', title='Library', brands=brands,categories=categories, products =products)

@main.route('/library/cat/writers', methods=['GET','POST'])
def book_cat_writers():
	brands = Brandname.query.all()
	categories = Catagoryname.query.all()
	products = Product.query.all()
	con=[]
	for brand in brands:
		con.append(0)
	i = 0
	for brand in brands:
		count = Product.query.filter_by(brand = brand.brand_name).all()
		count = len(count)
		con[i]=count
		i=+1

	return render_template('catalog.html',con =con, title='Writers', brands=brands,categories=categories, products =products)
    




@main.route('/library/cat/catagories', methods=['GET','POST'])
def book_cat_catagories():
	brands = Brandname.query.all()
	categories = Catagoryname.query.all()
	products = Product.query.all()
	con=[]
	for brand in categories:
		con.append(0)
	i = 0
	for brand in categories:
		count = Product.query.filter_by(category = brand.catagory_name).all()
		count = len(count)
		con[i]=count
		i=+1

	return render_template('catalog.html',con =con, title='categories', brands=brands,categories=categories, products =products)


@main.route('/book/<int:id>', methods=['GET','POST'])

def single_page(id):
	brands = Brandname.query.all()
	categories = Catagoryname.query.all()
	pro=Product.query.filter_by(id=id).first()

	return render_template('single_product.html', title=pro.name, brands=brands,categories=categories,pro=pro)


@main.route('/thanks')
def thanks():
    return render_template('thank.html')

@main.route('/dashboard/post/pending', methods=['GET','POST'])
@login_required
def dashboard_post_pending():
	if current_user.username == 'lampofcheer' or current_user.type == 'admin':
		a = 1
	elif current_user.status != 'approve':
		return "<h2>Please wait for account approve. it may take upto 12 hours.</h2>"
	post = Post.query.filter_by(status='pending').all()
	return render_template('dashboard_post_pending.html', title='dashboard' , posts = post)


@main.route('/dashboard/post/approve', methods=['GET','POST'])
@login_required
def dashboard_post_approve():
	if current_user.username == 'lampofcheer' or current_user.type == 'admin':
		a = 1
	elif current_user.status != 'approve':
		return "<h2>Please wait for account approve. it may take upto 12 hours.</h2>"
	post = Post.query.filter_by(status='approve').all()
	return render_template('dashboard_post_approve.html', title='dashboard' , posts = post)


@main.route('/dashboard/post/delete', methods=['GET','POST'])
@login_required
def dashboard_post_delete():
	if current_user.username == 'lampofcheer' or current_user.type == 'admin':
		a = 1
	elif current_user.status != 'approve':
		return "<h2>Please wait for account approve. it may take upto 12 hours.</h2>"
	post = Post.query.filter_by(status='delete').all()
	return render_template('dashboard_post_delete.html', title='dashboard' , posts = post)


@main.route('/dashboard/account/pending', methods=['GET','POST'])
@login_required
def dashboard_account_pending():
	if current_user.username == 'lampofcheer' or current_user.type == 'admin':
		a = 1
	elif current_user.status != 'approve':
		return "<h2>Please wait for account approve. it may take upto 12 hours.</h2>"
	post = User.query.filter_by(status='pending').all()
	return render_template('dashboard_account_pending.html', title='dashboard' , posts = post)


@main.route('/dashboard/account/approved', methods=['GET','POST'])
@login_required
def dashboard_account_approve():
	if current_user.username == 'lampofcheer' or current_user.type == 'admin':
		a = 1
	elif current_user.status != 'approve':
		return "<h2>Please wait for account approve. it may take upto 12 hours.</h2>"
	post = User.query.filter_by(status='approve').all()
	return render_template('dashboard_account_approve.html', title='dashboard' , posts = post)



@main.route('/dashboard/account/delete', methods=['GET','POST'])
@login_required
def dashboard_account_delete():
	if current_user.username == 'lampofcheer' or current_user.type == 'admin':
		a = 1
	elif current_user.status != 'approve':
		return "<h2>Please wait for account approve. it may take upto 12 hours.</h2>"
	post = User.query.filter_by(status='delete').all()
	return render_template('dashboard_account_delete.html', title='dashboard' , posts = post)


@main.route('/dashboard/blog', methods=['GET','POST'])
@login_required
def dashboard_blog():
	if current_user.username == 'lampofcheer' or current_user.type == 'admin':
		a = 1
	elif current_user.status != 'approve':
		return "<h2>Please wait for account approve. it may take upto 12 hours.</h2>"
	post = Blog.query.all()
	return render_template('dashboard_blog.html', title='dashboard' , posts = post)




@main.route('/dashboard/account/<int:id>/admin', methods=['GET','POST'])
@login_required
def admin_account_admin(id):
	if current_user.username == 'lampofcheer' or current_user.type == 'admin':
		a = 1
	elif current_user.status != 'approve':
		return "<h2>Please wait for account approve. it may take upto 12 hours.</h2>"
	if current_user.is_authenticated:
		if current_user.type == 'admin' or current_user.username == 'lampofcheer':
			brands = Brandname.query.all()
			categories = Catagoryname.query.all()
			post=User.query.filter_by(id=id).first()
			post.type = 'admin'
			db.session.commit()
			res = User.query.filter_by(type='admin')
			body = post.username +','+post.email+" by " + current_user.email + ' , ' + current_user.username
			send_email(res,'admin added',body)
			flash('Your post has been approved!', 'success')
			return redirect(url_for('main.dashboard_account_approve'))

	else:
			return "<h3>Admin Login Required.</h3>"


@main.route('/dashboard/account/<int:id>/panel', methods=['GET','POST'])
@login_required
def admin_account_panel(id):
	if current_user.username == 'lampofcheer' or current_user.type == 'admin':
		a = 1
	elif current_user.status != 'approve':
		return "<h2>Please wait for account approve. it may take upto 12 hours.</h2>"
	if current_user.is_authenticated:
		if current_user.type == 'admin' or current_user.username == 'lampofcheer':
			brands = Brandname.query.all()
			categories = Catagoryname.query.all()
			post=User.query.filter_by(id=id).first()
			post.type = 'panel'
			db.session.commit()
			res = User.query.filter_by(type='admin')
			body = post.username +','+post.email+" by " + current_user.email + ' , ' + current_user.username
			send_email(res,'panel added',body)
			flash('Your post has been approved!', 'success')
			return redirect(url_for('main.dashboard_account_approve'))

	else:
			return "<h3>Admin Login Required.</h3>"










































































'''@main.route("/weather")
def weather():
	if request.headers.getlist("X-Forwarded-For"):
		ip = request.headers.getlist("X-Forwarded-For")[0]
	else:
		ip = request.remote_addr
	country = get_country(ip)
	weather=call_api(country[3],country[4])
	return render_template('weather.html', title='weather' ,country=country,weather=weather)'''




'''@main.route('/addcart', methods=['POST'])
def AddCart():
	try:
		product_id = request.form.get('product_id')
		quantity = int(request.form.get('quantity'))
		color = request.form.get('colors')
		product = Product.query.filter_by(id=product_id).first()

		if request.method =="POST":
			DictItems = {product_id:{'name':product.name,'price':float(product.price),'discount':product.discount,'color':color,'quantity':quantity,'image':product.image_1, 'colors':product.colors}}
			if 'Shoppingcart' in session:
				#print(session['Shoppingcart'])
				if product_id in session['Shoppingcart']:
					for key, item in session['Shoppingcart'].items():
						if int(key) == int(product_id):
							session.modified = True
							item['quantity'] += 1
				else:
					session['Shoppingcart'] = MagerDicts(session['Shoppingcart'], DictItems)
					return redirect(request.referrer)
			else:
				session['Shoppingcart'] = DictItems
				return redirect(request.referrer)
              
	except Exception as e:
		print(e)
	finally:
		print(session['Shoppingcart'])
		return redirect(request.referrer)

@main.route('/carts')
def getCart():
	if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
		return redirect(url_for('main.index'))
	brands = Brandname.query.all()
	categories = Catagoryname.query.all()
	subtotal = 0
	grandtotal = 0
	for key,product in session['Shoppingcart'].items():
		discount = (float(product['discount'])/100) * float(product['price'])
		subtotal += float(product['price']) * int(product['quantity'])
		subtotal -= discount
		tax =("%.2f" %(.06 * float(subtotal)))
		grandtotal = float("%.2f" % (1.06 * subtotal))
	return render_template('cart.html',tax=tax, grandtotal=grandtotal,brands=brands,categories=categories)


@main.route('/updatecart/<int:code>', methods=['POST'])
def updatecart(code):
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return redirect(url_for('main.index'))
    if request.method =="POST":
        quantity = request.form.get('quantity')
        color = request.form.get('color')
        try:
            session.modified = True
            for key , item in session['Shoppingcart'].items():
                if int(key) == code:
                    item['quantity'] = quantity
                    item['color'] = color
                    flash('Item is updated!')
                    return redirect(url_for('main.getCart'))
        except Exception as e:
            print(e)
            return redirect(url_for('main.getCart'))

@main.route('/deleteitem/<int:id>')
def deleteitem(id):
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return redirect(url_for('main.index'))
    try:
        session.modified = True
        for key , item in session['Shoppingcart'].items():
            if int(key) == id:
                session['Shoppingcart'].pop(key, None)
                return redirect(url_for('main.getCart'))
    except Exception as e:
        print(e)
        return redirect(url_for('main.getCart'))

@main.route('/clearcart')
def clearcart():
    try:
        session.pop('Shoppingcart', None)
        return redirect(url_for('main.index'))
    except Exception as e:
        print(e)



def updateshoppingcart():
    for key, shopping in session['Shoppingcart'].items():
        session.modified = True
        del shopping['image']
        del shopping['colors']
    return updateshoppingcart


@main.route('/getorder')
@login_required
def get_order():
    if current_user.is_authenticated:
        customer_id = current_user.id
        invoice = secrets.token_hex(5)
        updateshoppingcart
        try:
            order = CustomerOrder(invoice=invoice,customer_id=customer_id,orders=session['Shoppingcart'])
            db.session.add(order)
            db.session.commit()
            session.pop('Shoppingcart')
            flash('Your order has been sent successfully','success')
            return redirect(url_for('main.orders',invoice=invoice))
        except Exception as e:
            print(e)
            flash('Some thing went wrong while get order', 'danger')
            return redirect(url_for('main.getCart'))





@main.route('/payment',methods=['POST'])
def payment():
    invoice = request.get('invoice')
    amount = request.form.get('amount')
    customer = stripe.Customer.create(
      email=request.form['stripeEmail'],
      source=request.form['stripeToken'],
    )
    charge = stripe.Charge.create(
      customer=customer.id,
      description='Ecoknowme',
      amount=amount,
      currency='usd',
    )
    orders =  CustomerOrder.query.filter_by(customer_id = current_user.id,invoice=invoice).order_by(CustomerOrder.id.desc()).first()
    orders.status = 'Paid'
    db.session.commit()
    return redirect(url_for('thanks'))






@main.route('/orders/<invoice>')
@login_required
def orders(invoice):
    if current_user.is_authenticated:
        grandTotal = 0
        subTotal = 0
        customer_id = current_user.id
        customer = User.query.filter_by(id=customer_id).first()
        orders = CustomerOrder.query.filter_by(customer_id=customer_id, invoice=invoice).order_by(CustomerOrder.id.desc()).first()
        for _key, product in orders.orders.items():
            discount = (float(product['discount'])/100) * float(product['price'])
            subTotal += float(product['price']) * int(product['quantity'])
            subTotal -= discount
            tax = ("%.2f" % (.06 * float(subTotal)))
            grandTotal = ("%.2f" % (1.06 * float(subTotal)))

    else:
        return redirect(url_for('customerLogin'))
    return render_template('order.html',title='invoice' ,invoice=invoice, tax=tax,subTotal=subTotal,grandTotal=grandTotal,customer=customer,orders=orders)



@main.route('/get_pdf/<invoice>', methods=['POST'])
@login_required
def get_pdf(invoice):
    if current_user.is_authenticated:
        grandTotal = 0
        subTotal = 0
        customer_id = current_user.id
        if request.method =="POST":
            customer = User.query.filter_by(id=customer_id).first()
            orders = CustomerOrder.query.filter_by(customer_id=customer_id, invoice=invoice).order_by(CustomerOrder.id.desc()).first()
            for _key, product in orders.orders.items():
                discount = (float(product['discount'])/100) * float(product['price'])
                subTotal += float(product['price']) * int(product['quantity'])
                subTotal -= discount
                tax = ("%.2f" % (.06 * float(subTotal)))
                grandTotal = float("%.2f" % (1.06 * subTotal))

            rendered =  render_template('pdf.html', invoice=invoice, tax=tax,grandTotal=grandTotal,customer=customer,orders=orders)
            pdf = pdfkit.from_string(rendered, False,configuration=config)
            response = make_response(pdf)
            response.headers['content-Type'] ='application/pdf'
            response.headers['content-Disposition'] ='inline; filename='+invoice+'.pdf'
            return response
    return request(url_for('main.orders'))'''










