-- Create totem_personalities table
CREATE TABLE IF NOT EXISTS totem_personalities (
    id SERIAL PRIMARY KEY,
    high_trait VARCHAR(50) NOT NULL,
    low_trait VARCHAR(50) NOT NULL,
    title VARCHAR(100) NOT NULL,
    animal VARCHAR(50) NOT NULL,
    emoji VARCHAR(10) NOT NULL,
    description TEXT NOT NULL,
    animal_qualities TEXT NOT NULL,
    motivational_message TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert all totem personalities data
INSERT INTO totem_personalities (high_trait, low_trait, title, animal, emoji, description, animal_qualities, motivational_message) VALUES
-- High Openness + Low [Trait]
('Openness', 'Conscientiousness', 'The Visionary', 'Octopus', '🐙', 'You''re a creative innovator who thrives on possibilities and new ideas, though you may struggle with routine and structure.', 'Like an octopus, you''re incredibly adaptable, intelligent, and able to see solutions others miss. You can squeeze through tight spots and approach problems from unique angles.', 'Embrace your creativity! Your unique perspective is your superpower.'),

('Openness', 'Extraversion', 'The Dreamer', 'Owl', '🦉', 'You''re a thoughtful contemplator who loves exploring ideas and concepts in your own quiet space.', 'Like an owl, you''re wise, observant, and see things others miss. You prefer the quiet hours for your deepest thinking and most creative insights.', 'Your quiet wisdom lights the way for others. Trust your inner voice.'),

('Openness', 'Agreeableness', 'The Maverick', 'Crow', '🐦‍⬛', 'You''re an independent thinker who challenges conventions and isn''t afraid to ruffle feathers for the sake of progress.', 'Like a crow, you''re highly intelligent, resourceful, and unafraid to be different. You see opportunities where others see obstacles.', 'Your independent spirit drives innovation. Keep questioning the status quo!'),

('Openness', 'Neuroticism', 'The Explorer', 'Dolphin', '🐬', 'You''re an adventurous spirit who approaches life with curiosity and emotional resilience.', 'Like a dolphin, you''re playful, intelligent, and emotionally balanced. You navigate life''s waters with grace and enthusiasm.', 'Dive deep into new experiences! Your calm confidence opens doors.'),

-- High Conscientiousness + Low [Trait]
('Conscientiousness', 'Openness', 'The Engineer', 'Beaver', '🦫', 'You''re a practical builder who creates lasting value through careful planning and steady execution.', 'Like a beaver, you''re industrious, reliable, and excellent at building strong foundations. Your methodical approach creates lasting impact.', 'Your steady progress builds mountains! Keep laying those solid foundations.'),

('Conscientiousness', 'Extraversion', 'The Strategist', 'Ant', '🐜', 'You''re a meticulous planner who prefers working behind the scenes to achieve long-term goals.', 'Like an ant, you''re incredibly organized, hardworking, and understand that small consistent efforts lead to big results.', 'Your discipline is your strength! Every small step leads to great achievements.'),

('Conscientiousness', 'Agreeableness', 'The Inspector', 'Wolf', '🐺', 'You''re a discerning leader who maintains high standards and isn''t afraid to make tough decisions.', 'Like a wolf, you''re loyal to your pack but fierce in protecting standards. You lead by example and command respect through competence.', 'Your standards elevate everyone around you. Lead with confidence!'),

('Conscientiousness', 'Neuroticism', 'The Pillar', 'Elephant', '🐘', 'You''re a steady, reliable force that others can always count on during challenging times.', 'Like an elephant, you''re wise, strong, and have an excellent memory. Your calm presence provides stability for your entire community.', 'You are the rock others lean on. Your strength gives others courage.'),

-- High Extraversion + Low [Trait]
('Extraversion', 'Openness', 'The Entertainer', 'Parrot', '🦜', 'You''re a charismatic performer who brings joy and energy to social situations through established, proven approaches.', 'Like a parrot, you''re social, expressive, and bring color to any gathering. You know how to communicate in ways that resonate with everyone.', 'Your enthusiasm is infectious! Keep spreading joy wherever you go.'),

('Extraversion', 'Conscientiousness', 'The Spark', 'Monkey', '🐵', 'You''re an energetic catalyst who brings spontaneity and fun to every situation, though you may struggle with follow-through.', 'Like a monkey, you''re playful, social, and full of energy. You swing from opportunity to opportunity with infectious enthusiasm.', 'Your energy lights up the room! Channel that spark into something amazing.'),

('Extraversion', 'Agreeableness', 'The Influencer', 'Peacock', '🦚', 'You''re a confident leader who isn''t afraid to stand out and take charge of situations.', 'Like a peacock, you''re confident, eye-catching, and naturally draw attention. You''re not afraid to display your talents proudly.', 'Your confidence inspires others! Own your spotlight and lead boldly.'),

('Extraversion', 'Neuroticism', 'The Optimist', 'Golden Retriever', '🐕', 'You''re an upbeat, social person who approaches life with enthusiasm and maintains a positive outlook.', 'Like a golden retriever, you''re friendly, loyal, and always see the best in people. Your positive energy is contagious and uplifting.', 'Your positivity is a gift to the world! Keep shining that bright light.'),

-- High Agreeableness + Low [Trait]
('Agreeableness', 'Openness', 'The Caretaker', 'Sheep', '🐑', 'You''re a nurturing supporter who finds fulfillment in caring for others through traditional, proven methods.', 'Like a sheep, you''re gentle, caring, and find strength in community. You prefer harmony and mutual support over conflict.', 'Your caring heart makes the world softer. Your kindness creates ripples of goodness.'),

('Agreeableness', 'Conscientiousness', 'The Helper', 'Rabbit', '🐰', 'You''re a spontaneous supporter who''s always ready to lend a hand, even if it means dropping your own plans.', 'Like a rabbit, you''re gentle, quick to respond to others'' needs, and bring a soft, caring energy wherever you go.', 'Your generous spirit touches so many lives! Remember to care for yourself too.'),

('Agreeableness', 'Extraversion', 'The Listener', 'Deer', '🦌', 'You''re a gentle, empathetic soul who prefers deep, meaningful connections over large social gatherings.', 'Like a deer, you''re sensitive, graceful, and highly attuned to others'' emotions. You move through life with quiet elegance.', 'Your gentle presence heals hearts. Your listening ear is a precious gift.'),

('Agreeableness', 'Neuroticism', 'The Peacemaker', 'Dove', '🕊️', 'You''re a calm mediator who naturally brings harmony and peace to conflicts and tense situations.', 'Like a dove, you''re peaceful, pure-hearted, and naturally bring calm to chaotic situations. You''re a symbol of hope for others.', 'Your peaceful spirit calms storms. You bring hope wherever you go.'),

-- High Neuroticism + Low [Trait]
('Neuroticism', 'Openness', 'The Worrier', 'Hedgehog', '🦔', 'You''re a cautious protector who prefers familiar territory and may worry about potential risks and changes.', 'Like a hedgehog, you''re naturally defensive and careful. When you feel safe, you reveal your softer, more vulnerable side.', 'Your caution keeps others safe. Trust yourself to slowly explore new territories.'),

('Neuroticism', 'Conscientiousness', 'The Alarmist', 'Mouse', '🐭', 'You''re highly sensitive to your environment and may feel overwhelmed by too many demands or changes at once.', 'Like a mouse, you''re quick to notice changes and potential threats. Your sensitivity helps you navigate complex social situations.', 'Your sensitivity is actually a superpower. Small steps lead to big changes.'),

('Neuroticism', 'Extraversion', 'The Loner', 'Cat', '🐱', 'You''re an independent soul who prefers solitude and may feel overwhelmed by too much social interaction.', 'Like a cat, you''re independent, selective about relationships, and need your own space to recharge. You''re deeply loyal to those you trust.', 'Your independence is strength. Take the space you need to shine in your own way.'),

('Neuroticism', 'Agreeableness', 'The Critic', 'Porcupine', '🦔', 'You''re a sharp-eyed evaluator who isn''t afraid to point out flaws, though you may struggle with emotional sensitivity.', 'Like a porcupine, you have a tough exterior that protects a sensitive core. Your sharp observations help improve everything around you.', 'Your critical eye drives excellence. Your insights make everything better.');

-- Create an index for faster lookups
CREATE INDEX IF NOT EXISTS idx_totem_personalities_traits ON totem_personalities(high_trait, low_trait);

-- Add a comment to the table
COMMENT ON TABLE totem_personalities IS 'Animal totem personalities based on Big Five (OCEAN) personality traits'; 