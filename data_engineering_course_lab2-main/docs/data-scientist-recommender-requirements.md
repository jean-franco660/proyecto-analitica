# Data Scientist Recommender Requirements Case Study

This document is a stakeholder interview scenario between a data engineer and a
data scientist about a personalized product recommendation system.

This conversation is important because it translates a machine learning idea
into concrete data engineering requirements: batch training data, model artifact
management, low-latency serving, streaming events, scalability, and output
logging.

## Scenario

The data engineer has already spoken with:

- Marketing, to understand dashboard and recommendation business needs.
- Software engineering, to understand safe access to source system data.

Now the data engineer returns to the data scientist to understand how the
recommender system should work and what data pipelines are needed to support it.

The recommendation project has two major data engineering needs:

- A batch pipeline to prepare training data.
- A low-latency streaming or serving pipeline to provide recommendations while
  users browse or check out.

## Stakeholder Interview

**Data engineer:** The last time we spoke, we talked about two projects you are
working on for the marketing team: an analytics dashboard and a recommender
system.

Since then, I talked to the product marketing manager to learn more about their
needs for each system, and I met with a software engineer from the platform team
to learn how we can access data from the sales platform.

What I would like to do now is learn more about how you imagine the recommender
system will work, so we can start prototyping the data pipeline to serve it. Can
you tell me more about your work so far?

**Data scientist:** Sure. I have been experimenting over the last month with
models and ideas for the recommender system.

For now, I have decided to implement a content-based recommender system. The way
it works is that I take a set of features containing information about each
product and another set of features containing information about each user.

Then I compute a vector embedding for each user and each product and look for
similarities between those embeddings to make product recommendations.

The model takes user and product features as input and generates a list of
product IDs as output.

**Data engineer:** So you already have something running?

**Data scientist:** Sort of. I have been experimenting with models on my local
machine. I trained a content-based recommender using user and product data that I
initially downloaded for the dashboards.

The model seems to be working okay. What I would like to try next is retraining
the model based on a fresh batch of data to see how stable it is and understand
how often we might want to retrain and update the model in deployment.

**Data engineer:** If you can tell me more about the format and structure you
need for the training data, I can start planning a batch data pipeline to deliver
that data.

**Data scientist:** The training data is tabular. Each row contains data for a
single product purchase.

The user feature columns are:

- `customer number`
- `credit limit`
- `city`
- `postal code`
- `country`

The product feature columns are:

- `product code`
- `quantity in stock`
- `buy price`
- `msrp`
- `product line`
- `product scale`

In addition to those user and product features, there is a rating value from 1
to 5 that represents the user's rating of that product.

**Data engineer:** If you had to guess, how frequently do you think you might
want to retrain and update the deployed model?

**Data scientist:** I am not sure yet. I plan to monitor the model's output.

It would be great if, in addition to serving recommendations on the platform, all
model output could be automatically saved for later analysis.

Then I would retrain the model if I notice drift in performance or changes in
the input data.

I might want to retrain as frequently as once a week, but it could also be less
frequent, like monthly or quarterly.

It would be great if delivering a new batch of training data does not require too
much operational overhead, even if we later modify the format to include new
product or user features.

**Data engineer:** That makes sense. Can you tell me more about how you expect
the recommender model to be used in production?

**Data scientist:** I would like to make recommendations based on user
information and information about products users have browsed or added to their
shopping cart.

The model should take user information and information about any number of
products they have been looking at as input.

Then it can find products to recommend based on the user information and
additional products to recommend based on the products they have browsed or put
in their cart.

**Data engineer:** How fast will the system need to generate recommendations?

**Data scientist:** We want to present recommended products more or less
instantaneously as users browse products or go through checkout.

A page usually takes a second or two to render, so if the recommender can work
that fast, that would be great.

**Data engineer:** How long does it take to run the model and generate
recommendations?

**Data scientist:** The model is very fast. On my local machine, it only takes a
few milliseconds to generate recommendations given input features.

I already have all vector embeddings for products in the catalog stored, so when
I run the model, I can quickly perform the similarity calculation.

**Data engineer:** As I understand it, the platform records user activity from
online users in an event log, so it should be possible to stream events from that
log with very low latency.

Assuming the sales platform can provide user and product data and then receive
and render product recommendations with sub-second latency, I may have about one
second to complete the full round trip: ingest, transform, serve user and product
features to the model, and return recommended product IDs back to the platform.

What about scalability? How many concurrent users do you expect to serve
recommendations to?

**Data scientist:** The company currently has around 100,000 customers in the
database. Many have bought at least one item, and many are repeat shoppers.

We expect that number to grow as the company expands to new regions and product
lines.

Activity varies a lot. Sometimes only a few people are shopping, but we can see
spikes of up to 10,000 users on the platform at the same time, and we could see
more in the future.

**Data engineer:** That gives me what I need for now. Thanks.

**Data scientist:** Great. Let me know if more questions come up.
