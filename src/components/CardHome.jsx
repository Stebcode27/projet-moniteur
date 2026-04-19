import './CardHome.css';

const CardHome = ({ title, description, image }) => {
  return (
    <div className="card-home">
        <img src={image} alt={title} className="card-image" />
        <div className="card-content">
            <h3 className="card-title">{title}</h3>
            <p className="card-description">{description}</p>
        </div>
    </div>
  );
}

export default CardHome;