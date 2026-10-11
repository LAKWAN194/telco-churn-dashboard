from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.schemas.customer import CustomerFeatures, ModelInfo, PredictionOut
from backend.services.db import Customer, Prediction, get_db
from backend.services.model import ChurnModel, get_model, risk_level

router = APIRouter(tags=["predictions"])


def to_prediction_out(prediction: Prediction) -> PredictionOut:
    return PredictionOut(
        prediction_id=prediction.prediction_id,
        customer_id=prediction.customer_id,
        churn_probability=round(prediction.churn_probability, 4),
        churn_prediction=prediction.churn_prediction,
        risk_level=risk_level(prediction.churn_probability, prediction.threshold_used),
        model_version=prediction.model_version,
        threshold_used=round(prediction.threshold_used, 4),
        predicted_at=prediction.predicted_at,
    )


def save_prediction(
    db: Session, model: ChurnModel, features: dict, customer_id: str | None
) -> Prediction:
    """
    Score one customer and record the result in the predictions table.

    Args:
        db (Session): The database session.
        model (ChurnModel): The trained model.
        features (dict): Feature name mapped to value.
        customer_id (str | None): The stored customer this is for, or None
            for a what-if prediction typed into the form.

    Returns:
        Prediction: The saved row, including its id and timestamp.
    """
    probability, will_churn = model.predict_one(features)

    prediction = Prediction(
        customer_id=customer_id,
        churn_probability=probability,
        churn_prediction=will_churn,
        model_version=model.version,
        threshold_used=model.threshold,
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    return prediction


@router.get("/model", response_model=ModelInfo)
def model_info(model: ChurnModel = Depends(get_model)):
    """Which model is serving predictions, and how it scored on the test set."""
    return ModelInfo(
        model_name=model.name,
        model_version=model.version,
        threshold=round(model.threshold, 4),
        trained_at=model.trained_at,
        features=model.features,
        metrics=model.metrics,
    )


@router.post("/predict", response_model=PredictionOut)
def predict(
    customer: CustomerFeatures,
    db: Session = Depends(get_db),
    model: ChurnModel = Depends(get_model),
):
    """Predict churn for customer details sent in the request body."""
    prediction = save_prediction(db, model, customer.model_dump(), customer_id=None)
    return to_prediction_out(prediction)


@router.post("/predict/{customer_id}", response_model=PredictionOut)
def predict_for_customer(
    customer_id: str,
    db: Session = Depends(get_db),
    model: ChurnModel = Depends(get_model),
):
    """Predict churn for a customer already in the database."""
    customer = db.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")

    features = {name: getattr(customer, name) for name in model.features}
    prediction = save_prediction(db, model, features, customer_id=customer_id)
    return to_prediction_out(prediction)


@router.get("/predictions", response_model=list[PredictionOut])
def recent_predictions(
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """The most recent predictions, newest first."""
    predictions = db.execute(
        select(Prediction)
        .order_by(Prediction.predicted_at.desc(), Prediction.prediction_id.desc())
        .limit(limit)
    ).scalars().all()

    return [to_prediction_out(prediction) for prediction in predictions]
