# CTO Requirements Gathering Case Study

This document is a stakeholder interview scenario between a newly hired data
engineer and the Chief Technology Officer. It helps students practice extracting
technical strategy, architectural constraints, and long-term data engineering
responsibilities from an executive-level conversation.

The CTO conversation is different from a data scientist conversation. The CTO is
less focused on one dashboard or one dataset, and more focused on company risk,
scalability, modernization, customer retention, and future platform direction.

## Scenario

A new data engineer joins an ecommerce company. The CTO explains the company's
major technology initiatives for the coming year:

- Expand market share.
- Add new product offerings.
- Grow internationally.
- Modernize legacy systems.
- Reduce outage risk.
- Move toward streaming data pipelines.
- Support machine learning and recommendation systems.

The data engineer's role is not only to build pipelines, but also to help the
software teams produce better data as the platform is refactored.

## Stakeholder Interview

**Data engineer:** Hi Matt, thanks for taking the time to chat with me today. I
am very excited to be starting at this company. One of the things I would like to
do is get a better understanding of the business goals and technology efforts
that you are working on.

**CTO:** Great to have you on board, Joe. I like to talk to all the new hires
within technology to make sure our goals are aligned. I know you probably will
not be able to talk to me all the times you would like to, but this is my
version of walking the shop floor to see what is happening.

For the coming year and beyond, your work as a data engineer is going to play a
key role in our success. I would like to explain how that ties into our larger
initiatives.

**Data engineer:** Sounds good.

**CTO:** So far, our company has been relatively successful as an ecommerce
platform across a limited number of product lines. We have done great marketing,
and because we were one of the first companies in the market, we had a first
mover advantage.

The challenge is that, as the market evolves, smaller brands are appearing and
taking market share.

Another major technology concern is that, although we are an ecommerce platform
now, we inherited old technology from before the company became a modern web
business. Some old code is still running, and there is concern that it could
cause outages. Those outages would be costly and damaging to our brand.

The big initiatives are expanding market share, adding new product offerings,
and going more international. All of that involves scale.

From the software side, we are planning to refactor. First, we want to remove the
old code that puts us at risk. Second, we want to make everything much more
scalable.

From your perspective as a data engineer, how would that affect you?

**Data engineer:** It could affect me greatly. I can think of several ways. I
know working with legacy tools is not always fun, but I am looking forward to
helping modernize the systems.

**CTO:** Exactly. That is the attitude I am looking for.

One of my major concerns is what I call the software-data divide. People write
code in a vacuum, and then data engineers have to consume whatever comes out.
That has been a big problem for us because the legacy code generates schemas
that are very hard to use for analytics.

As part of the team, I want you to consult with the software side as we refactor
our code. Help make sure that the output of the software is suitable for
analytics with minimal post-processing.

We will not remove all ETL, but if we generate data in the right way, with the
right schema, then the data will be much cleaner when it reaches analytics.

**Data engineer:** What tools can I expect to work with?

**CTO:** Part of this refactor is moving from a batch-based approach toward a
streaming-based approach.

On AWS, we are looking at Kinesis, which is Amazon's native streaming service.
We are also considering Kafka for certain pipelines as we scale.

Do you have experience with those?

**Data engineer:** I do not have production experience yet, but I studied data
engineering and worked with concepts like Kinesis and Kafka in labs. I am excited
to apply those ideas to real-world scenarios.

**CTO:** That is great.

At this stage, you will work as a consultant with the software side to understand
the data they produce and help them produce better quality data.

In the meantime, you can create proof-of-concept demonstrations of Kinesis and
Kafka, experiment with scalability, and build strong foundational skills. I see
one of your key future responsibilities as managing and expanding our streaming
capabilities.

You will do that under the direction of the head of data, but we expect you to
grow strong skills in this area.

**Data engineer:** I know AI is a hot topic. Does the company have any goals
around machine learning or AI?

**CTO:** One major goal is improving customer retention.

The core software refactor will help because it should produce a more responsive
website and less downtime. Avoiding downtime improves the customer experience.

In addition, we are working on a recommendation engine. Your part, within the
data engineering team, will be developing the data pipelines that feed that
recommendation engine.

That involves looking at our product taxonomy and also understanding how
customers behave on the site: clickstream data, order behavior, and other
activity. You will work with the data scientists to engineer the pipelines that
support that process.

**Data engineer:** Sounds great.

**CTO:** It is great to have you on board. I am excited to work with you, and I
hope we connect again as these initiatives progress.
