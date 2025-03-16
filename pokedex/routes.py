from pokedex import app, bcrypt, db
from flask import render_template, request, url_for, redirect, flash
from pokedex.models import User, PokemonType, Pokemon
from flask_login import login_user, logout_user, current_user, login_required



@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    pokemons = db.paginate(db.select(Pokemon), per_page=4, page=page)
    return render_template('index.html', title='Home Page', pokemons=pokemons)


@app.route('/game/<int:id>/detail')
def detail(id):
    pokemon = db.session.get(Pokemon, id)
    return render_template('detail_pokemon.html', title="Game's Detail Page", pokemon=pokemon)


@app.route('/game/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        user = db.session.scalar(db.select(User).where(User.username == username))
        if user:
            flash('User already exists!', 'warning')
        elif password == confirm_password:
            password_hash = bcrypt.generate_password_hash(password)
            user = User(username=username, email=email, password=password_hash)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
        else:
            flash('Password does not match!', 'warning')

    return render_template('user/register.html', title='Register Page')


@app.route('/game/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = db.session.scalar(db.select(User).where(User.username == username))
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password!', 'warning')

    return render_template('user/login.html', title='Login Page')


@app.route('/game/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/game/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')

        if firstname and lastname:
            current_user.firstname = firstname
            current_user.lastname = lastname
            db.session.commit()
            flash('User updated successfully!', 'success')
            return redirect(url_for('profile'))

    return render_template('user/profile.html', title='Profile Page')


@app.route('/game/type')
@login_required
def pokemon_types():
    types = db.session.scalars(db.select(PokemonType)).all()
    return render_template('type/index.html', title='Pokemon Type Page', types=types)


@app.route('/game/type/new', methods=['GET', 'POST'])
@login_required
def new_type():
    if request.method == 'POST':
        name = request.form.get('name')
        pokemon_type = PokemonType(name=name, user=current_user)
        db.session.add(pokemon_type)
        db.session.commit()
        flash('Added new Pokemon Type successfully!', 'success')
        return redirect(url_for('pokemon_types'))

    return render_template('type/new_type.html', title='Add New Pokemon Type')


@app.route('/game/type/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update_type(id):
    pokemon_type = db.session.get(PokemonType, id)
    if request.method == 'POST':
        pokemon_type.name = request.form.get('name')
        pokemon_type.user = current_user
        db.session.commit()
        flash('Updated Pokemon Type successfully!', 'success')
        return redirect(url_for('pokemon_types'))

    return render_template('type/update_type.html', title='Update Pokemon Type', type=pokemon_type)


@app.route('/game/game')
@login_required
def pokedex():
    search_query = request.args.get('search', '', type=str)
    page = request.args.get('page', 1, type=int)

    query = db.select(Pokemon)
    if search_query:
        query = query.where(Pokemon.name.ilike(f'%{search_query}%'))

    pokemons = db.paginate(query, per_page=4, page=page)

    return render_template('pokemon/index.html', title='Game Page', pokemons=pokemons, search_query=search_query)


@app.route('/game/game/new', methods=['GET', 'POST'])
@login_required
def new_pokemon():
    types = db.session.scalars(db.select(PokemonType)).all()
    if request.method == 'POST':
        name = request.form.get('name')
        weight = request.form.get('weight')
        height = request.form.get('height')
        description = request.form.get('description')
        img_url = request.form.get('img_url')

        pokemon_types = request.form.getlist('pokemon_types')
        type_objects = [db.session.get(PokemonType, int(type_id)) for type_id in pokemon_types]

        if db.session.scalar(db.select(Pokemon).where(Pokemon.name == name)):
            flash(f'{name} already exists!', 'warning')
        else:
            pokemon = Pokemon(
                name=name, weight=weight, height=height,
                description=description, img_url=img_url,
                user=current_user, types=type_objects
            )
            db.session.add(pokemon)
            db.session.commit()
            flash('Added new game successfully!', 'success')
            return redirect(url_for('pokedex'))

    return render_template('pokemon/new_pokemon.html', title='Add New Game Page', types=types)



@app.route('/pokedex/pokemon/<int:id>/detail')
@login_required
def pokemon_detail(id):
    pokemon = db.session.get(Pokemon, id)
    return render_template('pokemon/detail_pokemon.html', title="Game's Detail Page", pokemon=pokemon)


@app.route('/edit_pokemon/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_pokemon(id):
    pokemon = db.session.get(Pokemon, id)
    if request.method == 'POST':
        pokemon.name = request.form.get('name')
        pokemon.weight = request.form.get('weight')
        pokemon.height = request.form.get('height')
        pokemon.description = request.form.get('description')
        pokemon.img_url = request.form.get('img_url')

        db.session.commit()
        flash('Game updated successfully!', 'success')
        return redirect(url_for('pokemon_detail', id=id))

    return render_template('edit_pokemon.html', title='Edit Game', pokemon=pokemon)


@app.route('/delete_pokemon/<int:id>', methods=['POST'])
@login_required
def delete_pokemon(id):
    pokemon = db.session.get(Pokemon, id)
    if pokemon:
        db.session.delete(pokemon)
        db.session.commit()
        flash(f'{pokemon.name} has been deleted.', 'success')
    else:
        flash('Pokemon not found.', 'danger')

    return redirect(url_for('pokedex'))


